// #![feature(unboxed_closures)]
// #![feature(fn_traits)]
#![warn(unused_assignments)]
#![warn(confusable_idents)]

use std::collections::HashMap;
use std::ops::Range;
use std::panic;

use ndarray::{prelude::*, IntoDimension, stack};

use numpy::{
    IntoPyArray, PyArray1, PyReadonlyArray1, PyReadonlyArray2, PyReadonlyArray3, PyReadonlyArrayDyn, PyArray,
};
use pyo3::prelude::*;
use rand::distributions::Uniform;
use rand::Rng;
use rayon::prelude::*;

mod cost_utils;
mod optimisers;
mod pre_processing;
mod pricing_models;
mod tests;

use crate::cost_utils::{
    cost, cost_general, coverage, coverage_general, underutilisation, underutilization_general,
};
use crate::optimisers::{
    default_optimiser, default_optimiser_details, inertial_optimiser, simple_optimiser, Results, simple_optimiser_details,
};
use crate::pre_processing::{create_space, create_steps, CostFunction, CostPredictionFunction};
use crate::pricing_models::{PricingModel, Term};

#[pyclass(unsendable, frozen)]
#[derive(Clone)]
pub struct FinalResults {
    pub commitments: HashMap<String, ArrayBase<ndarray::OwnedRepr<usize>, Dim<[usize; 1]>>>,
    #[pyo3(get)]
    pub n_iter: usize,
    #[pyo3(get)]
    pub minimum: f64,
    #[pyo3(get)]
    pub coverage: f64,
    #[pyo3(get)]
    pub underutilization_cost: f64,
    #[pyo3(get)]
    pub step_size: Option<f64>,
    #[pyo3(get)]
    pub convergence: Convergence,
}

#[pymethods]
impl FinalResults {
    #[getter]
    fn commitments<'py>(
        &self,
        py: Python<'py>,
    ) -> HashMap<String, &'py numpy::PyArray<usize, Dim<[usize; 1]>>> {
        let mut dict: HashMap<String, &numpy::PyArray<usize, Dim<[usize; 1]>>> = HashMap::new();
        for (k, v) in self.commitments.clone() {
            dict.insert(k, v.into_pyarray(py));
        }

        dict
    }
}

#[derive(Clone, Default)]
#[pyclass(unsendable, frozen)]
pub struct Convergence {
    costs: Option<Vec<f64>>,
    coverages: Option<Vec<f64>>,
    discounts: Option<Vec<f64>>,
    choices: Option<Vec<usize>>,
    underutilisation_cost: Option<Vec<f64>>,
    speeds: Option<Vec<f64>>,
}

#[pymethods]
impl Convergence {
    #[getter]
    fn underutilisation_cost<'py>(&self, py: Python<'py>) -> Option<&'py PyArray1<f64>> {
        match &self.underutilisation_cost {
            Some(c) => Some(c.clone().into_pyarray(py)),
            None => None,
        }
    }
    #[getter]
    fn costs<'py>(&self, py: Python<'py>) -> Option<&'py PyArray1<f64>> {
        match &self.costs {
            Some(c) => Some(c.clone().into_pyarray(py)),
            None => None,
        }
    }
    #[getter]
    fn coverages<'py>(&self, py: Python<'py>) -> Option<&'py PyArray1<f64>> {
        match &self.coverages {
            Some(c) => Some(c.clone().into_pyarray(py)),
            None => None,
        }
    }
    #[getter]
    fn discounts<'py>(&self, py: Python<'py>) -> Option<&'py PyArray1<f64>> {
        match &self.discounts {
            Some(c) => Some(c.clone().into_pyarray(py)),
            None => None,
        }
    }
    #[getter]
    fn speeds<'py>(&self, py: Python<'py>) -> Option<&'py PyArray1<f64>> {
        match &self.speeds {
            Some(c) => Some(c.clone().into_pyarray(py)),
            None => None,
        }
    }
    #[getter]
    fn choices<'py>(&self, py: Python<'py>) -> Option<&'py PyArray1<usize>> {
        match &self.choices {
            Some(c) => Some(c.clone().into_pyarray(py)),
            None => None,
        }
    }
}

impl Convergence {
    pub fn new() -> Self {
        Convergence {
            costs: Some(Vec::new()),
            coverages: Some(Vec::new()),
            discounts: Some(Vec::new()),
            choices: Some(Vec::new()),
            underutilisation_cost: Some(Vec::new()),
            speeds: Some(Vec::new()),
        }
    }
}


fn finalise_results(
    res: Results,
    models: &Vec<PricingModel>,
    coverage: f64,
    underutilization_cost: f64,
    step_size: Option<f64>
) -> FinalResults {
    let mut returned_df: HashMap<String, ArrayBase<ndarray::OwnedRepr<usize>, Dim<[usize; 1]>>> =
        HashMap::new();

    let mut j = 0;
    for model in models {
        match model {
            PricingModel::Reservations(t, prices, _) => {
                let n = prices.len();
                let mut r = Array1::zeros(n + 1);
                r.slice_mut(s![1..]).assign(&res.argmin.slice(s![j..j + n]));
                match t {
                    Term::OneYear => {
                        returned_df.insert(String::from("one_year_commitments"), r);
                    }
                    Term::ThreeYears => {
                        returned_df.insert(String::from("three_years_commitments"), r);
                    }
                    Term::AlreadyPayed => continue,
                }
                j += n;
            }
            PricingModel::SavingsPlans(t, prices, _) => {
                let n = prices.len();
                let p = match t {
                    Term::OneYear => "one_year_commitments",
                    Term::ThreeYears => "three_years_commitments",
                    Term::AlreadyPayed => continue,
                };
                match returned_df.get_mut(p) {
                    Some(v) => v[0] = res.argmin[j],
                    None => {
                        let mut v = Array1::zeros(n + 1);
                        v[0] = res.argmin[j];
                        returned_df.insert(String::from(p), v);
                    }
                }
                j += 1;
            }
            PricingModel::OnDemand(_) => (),
        }
    }

    FinalResults {
        commitments: returned_df,
        n_iter: res.n_iter,
        coverage: coverage,
        underutilization_cost: underutilization_cost,
        minimum: res.minimum,
        step_size: step_size,
        convergence: res.convergence,
    }
}

#[pymodule]
fn rust_as_backend(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    #[pyo3(name = "simple_optimisation")]
    fn py_simple_optimiser<'py>(
        usage: PyReadonlyArray2<f64>,
        prices: PyReadonlyArray2<f64>,
        period: &str,
        horizon: &str,
        convergence_details: Option<bool>,
        step: Option<f64>,
        starting_point: Option<PyReadonlyArray1<f64>>,
    ) -> Py<FinalResults> {
        let usage = usage.as_array();
        let prices = prices.as_array();
        let (i, j) = usage.dim();

        let p = match period {
            "D" => 24.,
            "H" => 1.,
            _ => {
                panic!("provide a valid period string : either D or H")
            }
        };

        let od_prices = prices.slice(s![0, ..]);
        let average_cost = (&usage * &od_prices).sum() / i as f64;
        let t = match step {
            Some(t) => t,
            None => average_cost / 5_000.,
        };

        let space = create_space(usage.view(), prices.view(), p);
        let steps = create_steps(prices.view(), t, p);

        let start = match starting_point {
            Some(t) => t.as_array().to_owned(),
            None => Array1::from_iter(space.iter().map(|x| x.start)),
        };

        let mut normalisation: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 1]>> =
            Array1::ones(j + 1);
        normalisation
            .slice_mut(s![1..])
            .assign(&(Array1::zeros(j) + p));

        let make_cost_function = || {
            let mut two_dim_levels = Array2::zeros((i, j + 1));
            let mut dump = Array2::zeros((i, j));
            let normalisation = normalisation.clone();
            move |x: ArrayView1<f64>| {
                two_dim_levels.assign(&(&x * &normalisation));
                cost(usage, prices, two_dim_levels.view(), &mut dump)
            }
        };

        let make_record_function = || {
            let mut two_dim_levels = Array2::zeros((i, j + 1));
            let mut dump = Array2::zeros((i, j));
            let normalisation = normalisation.clone();
            move |convergence: &mut Convergence, x: ArrayView1<f64>, cost: f64| {
                two_dim_levels.assign(&(&x * &normalisation));
                let cov = coverage(usage.view(), prices, two_dim_levels.view(), &mut dump);
                let underu =
                    underutilisation(usage.view(), prices, two_dim_levels.view(), &mut dump);

                let message = "You haven't correctly initialized this Convergence object. Use Convergence::new() instead";

                convergence.costs.as_mut().expect(message).push(cost);
                convergence.coverages.as_mut().expect(message).push(cov);
                convergence
                    .underutilisation_cost
                    .as_mut()
                    .expect(message)
                    .push(underu);
            }
        };

        let res = match convergence_details {
            Some(true) => simple_optimiser_details(
                &mut make_cost_function(),
                steps.view(),
                start,
                &mut make_record_function()),
            _ => simple_optimiser(
                &mut make_cost_function(),
                steps.view(),
                start,
            ),
        };

   
        // println!("rust argmin : {:?}", res.argmin);

        let x = normalisation * res.argmin.mapv(|x: usize| x as f64);
        let argmin = Array2::zeros((i, j + 1)) + x;

        let mut returned_df: HashMap<
            String,
            ArrayBase<ndarray::OwnedRepr<usize>, Dim<[usize; 1]>>,
        > = HashMap::new();

        let key = match horizon {
            "3Y" => "three_years_commitments",
            "1Y" => "one_year_commitments",
            _ => panic!("Not a valid period, provide 3Y or 1Y"),
        };

        returned_df.insert(String::from(key), res.argmin);

        let mut dump = usage.to_owned();

        let fres = FinalResults {
            commitments: returned_df,
            n_iter: res.n_iter,
            coverage: coverage(usage.view(), prices, argmin.view(), &mut dump),
            underutilization_cost: underutilisation(usage.view(), prices, argmin.view(), &mut dump),
            minimum: res.minimum,
            step_size: Some(t),
            convergence: res.convergence,
        };

        Python::with_gil(|py| Py::new(py, fres).unwrap())
    }

    #[pyfn(m)]
    #[pyo3(name = "optimise_predictions")]
    fn py_optimise_predictions(
        predictions: PyReadonlyArray3<f64>,
        prices: PyReadonlyArray2<f64>,
        current_sp_commitments: PyReadonlyArray2<f64>,
        pricing_models: Vec<&str>,
        period: &str,
        n_starts: usize,
        convergence_details: Option<bool>,
    ) -> Py<FinalResults> {
        let predictions = predictions.as_array().to_owned();
        let (_, timespan, n) = predictions.dim();
        let prices = prices.as_array().to_owned();

        let days = period == "D";
        let period = match period {
            "D" => 24.,
            "H" => 1.,
            _ => {
                panic!("provide a valid period string : either D or H")
            }
        };
        let sp_levels = current_sp_commitments.as_array();

        let mut models = Vec::with_capacity(pricing_models.len());
        let max_usage = predictions.fold_axis(Axis(0), -f64::INFINITY, |a, &x| a.max(x));
        let max_usage = max_usage.fold_axis(Axis(0), -f64::INFINITY, |a, &x| a.max(x));

        let mut j = 0;
        let mut sp_index = 0;
        let mut space = Vec::with_capacity(n + 1);

        let null_base_level = Array2::zeros((timespan, n));

        for (i, p) in pricing_models.into_iter().enumerate() {
            let model = match p {
                "OD" => PricingModel::OnDemand(prices.slice(s![i, ..])),
                "RI1Y" => PricingModel::Reservations(
                    Term::OneYear,
                    prices.slice(s![i, ..]),
                    null_base_level.view(),
                ),
                "RI3Y" => PricingModel::Reservations(
                    Term::ThreeYears,
                    prices.slice(s![i, ..]),
                    null_base_level.view(),
                ),
                _ if p.contains("payed_") => PricingModel::SavingsPlans(
                    Term::AlreadyPayed,
                    prices.slice(s![i, ..]),
                    sp_levels.slice(s![.., sp_index]),
                ),
                "SP1Y" => PricingModel::SavingsPlans(
                    Term::OneYear,
                    prices.slice(s![i, ..]),
                    null_base_level.slice(s![.., 0]),
                ),
                "SP3Y" => PricingModel::SavingsPlans(
                    Term::ThreeYears,
                    prices.slice(s![i, ..]),
                    null_base_level.slice(s![.., 0]),
                ),
                _ => panic!("Not a known pricing model"),
            };

            match model {
                PricingModel::Reservations(Term::OneYear, _, _)
                | PricingModel::Reservations(Term::ThreeYears, _, _) => {
                    space.reserve(n);
                    for k in max_usage.iter() {
                        space.push(Range {
                            start: 0.,
                            end: k / period + 0.0000001,
                        })
                    }
                    j += n;
                }
                PricingModel::SavingsPlans(Term::OneYear, sp_prices, _)
                | PricingModel::SavingsPlans(Term::ThreeYears, sp_prices, _) => {
                    j += 1;
                    let max_sp = (&predictions * &sp_prices)
                        .sum_axis(Axis(0))
                        .fold(-f64::INFINITY, |a, &b| a.max(b));

                    space.push(Range {
                        start: 0.,
                        end: max_sp / period,
                    });
                }
                PricingModel::SavingsPlans(Term::AlreadyPayed, _, _) => {
                    sp_index += 1;
                }
                _ => (),
            }

            models.push(model);
        }
        models.sort();

        let record = match convergence_details {
            Some(b) => b,
            None => false,
        };

        let starts_vec: Vec<f64> = space
            .iter()
            .map(|x| {
                let range = Uniform::from(x.clone());
                let mut tmp: Vec<f64> = rand::thread_rng()
                    .sample_iter(&range.clone())
                    .take(n_starts)
                    .collect();
                tmp.push(0.);
                tmp.into_iter()
            })
            .flatten()
            .collect();

        let starts = unsafe { Array2::from_shape_vec_unchecked((j, n_starts + 1), starts_vec) };

        // let panicker = || {
        //     match py.check_signals() {
        //         Err(_) => panic!("keyboard interupt"),
        //         Ok(_)  => {},
        //     }
        // };

        // let panick_function = Arc::new(Mutex::new(panicker));

        let mut results = Vec::with_capacity(n_starts);
        starts
            .axis_iter(Axis(1))
            .into_par_iter()
            .map_init(
                || CostPredictionFunction::new(predictions.clone(), &models, days, record),
                |local_cost_function, start| inertial_optimiser(local_cost_function, start),
            )
            .collect_into_vec(&mut results);

        let res = results.iter().min().expect("not an empty set").to_owned();

        let x = res.argmin.mapv(|x: usize| x as f64);
        let mut dump = Array2::zeros((timespan, n));
        let coverages: Array1<f64> = predictions
            .axis_iter(Axis(0))
            .map(|pred| coverage_general(pred.view(), &models, x.view(), days, &mut dump))
            .collect();

        let underutils: Array1<f64> = predictions
            .axis_iter(Axis(0))
            .map(|pred| underutilization_general(pred.view(), &models, x.view(), days, &mut dump))
            .collect();

        let cov = coverages.sum() / coverages.len() as f64;

        let underutil = underutils.sum() / underutils.len() as f64;

        let fres = finalise_results(res, &models, cov, underutil, Some(1.));

        Python::with_gil(|py| Py::new(py, fres).unwrap())
    }

    #[pyfn(m)]
    #[pyo3(name = "cost")]
    fn py_cost(
        usage: PyReadonlyArray2<f64>,
        prices: PyReadonlyArray2<f64>,
        levels: PyReadonlyArrayDyn<'_, f64>,
    ) -> Option<f64> {
        let usage = usage.as_array();
        let prices = prices.as_array();

        let mut dump = usage.to_owned();
        let levels = levels.as_array().to_owned();

        let z = match levels.dim().into_dimension().ndim() {
            1 => {
                let (i, j) = usage.dim();
                let one_dim_levels = levels.into_dimensionality::<Ix1>().unwrap();
                let two_dim_levels = Array2::zeros((i, j + 1)) + &one_dim_levels;
                Some(cost(usage, prices, two_dim_levels.view(), &mut dump))
            }
            2 => Some(cost(
                usage,
                prices,
                levels.into_dimensionality::<Ix2>().unwrap().view(),
                &mut dump,
            )),
            _ => None,
        };

        z
    }

    #[pyfn(m)]
    #[pyo3(name = "coverage")]
    fn py_coverage(
        usage: PyReadonlyArray2<f64>,
        prices: PyReadonlyArray2<f64>,
        levels: PyReadonlyArrayDyn<'_, f64>,
    ) -> Option<f64> {
        let usage = usage.as_array();
        let mut dump = usage.to_owned();
        let prices = prices.as_array();

        let levels = levels.as_array().to_owned();

        let z = match levels.dim().into_dimension().ndim() {
            1 => {
                let (i, j) = usage.dim();
                let one_dim_levels = levels.into_dimensionality::<Ix1>().unwrap();
                let two_dim_levels = Array2::zeros((i, j + 1)) + &one_dim_levels;
                Some(coverage(
                    usage.view(),
                    prices.view(),
                    two_dim_levels.view(),
                    &mut dump,
                ))
            }
            2 => Some(coverage(
                usage.view(),
                prices.view(),
                levels.into_dimensionality::<Ix2>().unwrap().view(),
                &mut dump,
            )),
            _ => None,
        };

        z
    }

    #[pyfn(m)]
    #[pyo3(name = "general_optimisation")]
    fn py_optim_final(
        usage: PyReadonlyArray2<f64>,
        prices: PyReadonlyArray2<f64>,
        current_sp_commitments: PyReadonlyArray2<f64>,
        pricing_models: Vec<&str>,
        period: &str,
        n_starts: usize,
        optimiser: &str,
        convergence_details: Option<bool>,
        step_size: Option<f64>,
    ) -> Py<FinalResults> {
        let days = period == "D";
        let period = match period {
            "D" => 24.,
            "H" => 1.,
            _ => {
                panic!("provide a valid period string : either D or H")
            }
        };
        let usage = usage.as_array().to_owned();
        let prices = prices.as_array().to_owned();
        let sp_levels = current_sp_commitments.as_array();

        let mut models = Vec::with_capacity(pricing_models.len());
        let max_usage = usage.fold_axis(Axis(0), -f64::INFINITY, |a, &x| a.max(x));

        let (timespan, n) = usage.dim();
        let mut j = 0;
        let mut sp_index = 0;
        let mut space = Vec::with_capacity(n + 1);

        let null_base_level = Array2::zeros((timespan, n));

        for (i, p) in pricing_models.into_iter().enumerate() {
            let model = match p {
                "OD" => PricingModel::OnDemand(prices.slice(s![i, ..])),
                "RI1Y" => PricingModel::Reservations(
                    Term::OneYear,
                    prices.slice(s![i, ..]),
                    null_base_level.view(),
                ),
                "RI3Y" => PricingModel::Reservations(
                    Term::ThreeYears,
                    prices.slice(s![i, ..]),
                    null_base_level.view(),
                ),
                _ if p.contains("payed_") => PricingModel::SavingsPlans(
                    Term::AlreadyPayed,
                    prices.slice(s![i, ..]),
                    sp_levels.slice(s![.., sp_index]),
                ),
                "SP1Y" => PricingModel::SavingsPlans(
                    Term::OneYear,
                    prices.slice(s![i, ..]),
                    null_base_level.slice(s![.., 0]),
                ),
                "SP3Y" => PricingModel::SavingsPlans(
                    Term::ThreeYears,
                    prices.slice(s![i, ..]),
                    null_base_level.slice(s![.., 0]),
                ),
                _ => panic!("Not a known pricing model"),
            };

            match model {
                PricingModel::Reservations(Term::OneYear, _, _)
                | PricingModel::Reservations(Term::ThreeYears, _, _) => {
                    space.reserve(n);
                    for k in max_usage.iter() {
                        space.push(Range {
                            start: 0.,
                            end: k / period + 0.0000001,
                        })
                    }
                    j += n;
                }
                PricingModel::SavingsPlans(Term::OneYear, sp_prices, _)
                | PricingModel::SavingsPlans(Term::ThreeYears, sp_prices, _) => {
                    j += 1;
                    let max_sp = (&usage * &sp_prices)
                        .sum_axis(Axis(1))
                        .fold(-f64::INFINITY, |a, &b| a.max(b));
                    space.push(Range {
                        start: 0.,
                        end: max_sp / period,
                    });
                }
                PricingModel::SavingsPlans(Term::AlreadyPayed, _, _) => {
                    sp_index += 1;
                }
                _ => (),
            }

            models.push(model);
        }
        models.sort();

        // println!("{:?}", models);

        let record = match convergence_details {
            Some(b) => b,
            None => false,
        };

        let starts_vec: Vec<f64> = space
            .iter()
            .map(|x| {
                let range = Uniform::from(x.clone());
                let mut tmp: Vec<f64> = rand::thread_rng()
                    .sample_iter(&range.clone())
                    .take(n_starts)
                    .collect();
                tmp.push(0.);
                tmp.into_iter()
            })
            .flatten()
            .collect();

        let starts = unsafe { Array2::from_shape_vec_unchecked((j, n_starts + 1), starts_vec) };

        // let panicker = || {
        //     match py.check_signals() {
        //         Err(_) => panic!("keyboard interupt"),
        //         Ok(_)  => {},
        //     }
        // };

        // let panick_function = Arc::new(Mutex::new(panicker));

        // let mut results = Vec::with_capacity(n_starts);
        // starts
        //     .axis_iter(Axis(1))
        //     .into_par_iter()
        //     .map_init(
        //         || CostFunction::new(usage.clone(), &models, days, record),
        //         |local_cost_function, start| inertial_optimiser(local_cost_function, start),
        //     )
        //     .collect_into_vec(&mut results);

        // let res = results.iter().min().expect("not an empty set").to_owned();

        let levels = starts.slice(s![.., n_starts]);
        let mut c = CostFunction::new(usage.clone(), &models, days, record, step_size);
        let mut t = Some(c.step_size);
        let res = match optimiser {
            "inertial" => {
                t = None;
                inertial_optimiser(&mut c, levels.view())
            },
            _ => {
                let steps = c.steps.clone();
                match c.record {
                    false => default_optimiser(&mut c, steps.view(), levels),
                    true => default_optimiser_details(&mut c, steps.view(), levels)
                }
            }
        };

        let x = res.argmin.mapv(|x: usize| x as f64);
        let mut dump = usage.clone();

        let cov = coverage_general(usage.view(), &models, x.view(), days, &mut dump);
        let underutil = underutilization_general(usage.view(), &models, x.view(), days, &mut dump);
        
        let fres = finalise_results(res, &models, cov, underutil, t);
        Python::with_gil(|py| Py::new(py, fres).unwrap())
    }

    #[pyfn(m)]
    #[pyo3(name = "final_cost_coverage_underutilization")]
    fn py_cost_final(
        usage: PyReadonlyArray2<f64>,
        prices: PyReadonlyArray2<f64>,
        levels: PyReadonlyArray2<f64>,
        pricing_models: Vec<&str>,
        period: &str,
        cost_or_coverage: &str,
    ) -> f64 {
        let days = period == "D";
        let usage = usage.as_array();
        let prices = prices.as_array();
        let levels = levels.as_array().to_owned().mapv(|x| x as f64);

        let mut models = Vec::with_capacity(pricing_models.len());
        let (timespan, n) = usage.dim();
        let mut dump = Array2::zeros((timespan, n));
        let mut j = 0;
        for (i, p) in pricing_models.into_iter().enumerate() {
            let model = match p {
                "OD" => PricingModel::OnDemand(prices.slice(s![i, ..])),
                "RI1Y" => PricingModel::Reservations(
                    Term::OneYear,
                    prices.slice(s![i, ..]),
                    levels.slice(s![.., j..j + n])),
                "RI3Y" => PricingModel::Reservations(
                    Term::ThreeYears,
                    prices.slice(s![i, ..]),
                    levels.slice(s![.., j..j + n])),
                "SP1Y" => PricingModel::SavingsPlans(
                    Term::OneYear,
                    prices.slice(s![i, ..]),
                    levels.slice(s![.., j]),
                ),
                "SP3Y" => PricingModel::SavingsPlans(
                    Term::ThreeYears,
                    prices.slice(s![i, ..]),
                    levels.slice(s![.., j]),
                ),
                _ => panic!("Not a known pricing model"),
            };
            match model {
                PricingModel::Reservations(_, _, _) => j += n,
                PricingModel::SavingsPlans(_, _, _) => j += 1,
                _ => (),
            }

            models.push(model);
        }

        models.sort();

        let x = Array1::zeros(j);

        match cost_or_coverage {
            "cost" => cost_general(usage, &models, x.view(), days, &mut dump),
            "coverage" => coverage_general(usage.view(), &models, x.view(), days, &mut dump),
            "underutilization" => underutilization_general(usage, &models, x.view(), days, &mut dump),
            _ => panic!("not a valid operation")
        }
    }


    #[pyfn(m)]
    #[pyo3(name = "generate_cost_and_coverage")]
    fn py_monte_carlo<'py>(
        py: Python<'py>,
        usage: PyReadonlyArray2<f64>,
        prices: PyReadonlyArray2<f64>,
        n_sample: usize,
        n_threads: usize,
        period: &str,
    ) -> &'py PyArray<f64, ndarray::Dim<[usize; 2]>> {
        let usage = usage.as_array();
        let prices = prices.as_array();

        let (timespan, n) = usage.dim();

        let p = match period {
            "D" => 24.,
            __ => 1.
        };

        let space = create_space(usage.view(), prices.view(), 1.);

        let starts_vec: Vec<f64> = space
            .iter()
            .map(|x| {
                let boundaries = Range { start: 0., end:  x.end };
                let range = Uniform::from(boundaries);
                let mut tmp: Vec<f64> = rand::thread_rng()
                    .sample_iter(&range.clone())
                    .take(n_sample)
                    .collect();
                tmp.push(0.);
                tmp.into_iter()
            })
            .flatten()
            .collect();

        let starts = unsafe { Array2::from_shape_vec_unchecked((n + 1, n_sample), starts_vec) };

        let mut costs = Vec::with_capacity(n_sample);
        starts
            .axis_iter(Axis(1))
            .into_par_iter()
            .with_min_len(n_sample / n_threads)
            .map_init(
                || (usage.to_owned(), Array2::zeros((timespan, n + 1))),
                |(dump, levels), x| {
                    (*levels).assign(&x);
                    cost(usage, prices, levels.view(), dump)
                },
            )
            .collect_into_vec(&mut costs);

        let mut coverages = Vec::with_capacity(n_sample);
        starts
            .axis_iter(Axis(1))
            .into_par_iter()
            .with_min_len(n_sample / n_threads)
            .map_init(
                || (usage.to_owned(), Array2::zeros((timespan, n + 1))),
                |(dump, levels), x| {
                    (*levels).assign(&x);
                    coverage(usage, prices, levels.view(), dump)
                },
            )
            .collect_into_vec(&mut coverages);

        let a = Array1::from_vec(costs);
        let b = Array1::from_vec(coverages);

        let r = stack(Axis(1), &[a.view(), b.view()])
        .expect("cost and coverages don't have the same size");

        r.to_owned().into_pyarray(py)

    }

    m.add_class::<Results>()?;

    Ok(())
}
