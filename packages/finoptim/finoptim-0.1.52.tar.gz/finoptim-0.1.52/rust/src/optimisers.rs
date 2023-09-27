#![warn(confusable_idents)]

// use std::sync::{Arc, Mutex};
use std::cmp::Ordering;

use ndarray::prelude::*;
use ndarray::Axis;
use ndarray_stats::QuantileExt;
use numpy::{IntoPyArray, PyArray1};
use pyo3::prelude::*;
use pyo3::ffi::PyErr_CheckSignals;

use argminmax::ArgMinMax;

use crate::Convergence;

#[macro_export]
macro_rules! python_interupt {
    ($n_iter: expr, $period: expr) => {
        if $n_iter % $period == 0 {
            unsafe {if PyErr_CheckSignals() == -1 {panic!("Keyboard interupt");}}
        }
    };
}

pub trait Optimisable {
    fn call(&mut self, _x: ArrayView1<f64>) -> f64 {
        0.
    }

    fn gradient(&mut self, x: ArrayView1<f64>) -> Array1<f64> {
        Array1::zeros(x.len())
    }

    fn cost_variations(&mut self, x: ArrayView1<f64>) -> Array1<f64> {
        Array1::zeros(x.len())
    }

    fn record(&mut self, _x: ArrayView1<f64>, _c: f64, _speed: Option<f64>) {}

    fn should_record(&self) -> bool {
        false
    }

    fn dump_records(&self) -> Convergence {
        Convergence::default()
    }
}

#[pyclass(unsendable, frozen)]
#[derive(Clone)]
pub struct Results {
    pub argmin: Array1<usize>,
    #[pyo3(get)]
    pub n_iter: usize,
    #[pyo3(get)]
    pub minimum: f64,
    #[pyo3(get)]
    pub convergence: Convergence,
}

impl Ord for Results {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.minimum < other.minimum {
            true => Ordering::Less,
            false => {
                if self.minimum == other.minimum {
                    Ordering::Equal
                } else {
                    Ordering::Greater
                }
            }
        }
    }
}

impl PartialOrd for Results {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Results {
    fn eq(&self, other: &Self) -> bool {
        self.minimum == other.minimum
    }
}

impl Eq for Results {}

#[pymethods]
impl Results {
    #[getter]
    fn argmin<'py>(&self, py: Python<'py>) -> &'py PyArray1<usize> {
        self.argmin.clone().into_pyarray(py)
        // currently there's a copy here everytime Python wants to read this array
        // really not great
    }
}

fn l2_norm(x: ArrayView1<f64>) -> f64 {
    x.dot(&x).sqrt()
}

fn rounding<T: FnMut(ArrayView1<f64>) -> f64>(
    function: &mut T,
    point: ArrayView1<f64>,
) -> Array1<usize> {
    let mut x = point.to_owned();
    let n = point.len();

    let h: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 2]>> =
        Array2::from_diag(&Array1::ones(n));

    let mut grad = |x: ArrayView1<f64>| {
        let mut tmp = &h + &x;
        let c = function(x);
        tmp.map_axis_mut(Axis(1), |row| function(row.view()) - c)
    };

    let cost_variations = grad(point.view());

    let mut indices = (0..n).collect::<Vec<_>>();
    indices.sort_by(|&a, &b| {
        cost_variations[a]
            .partial_cmp(&cost_variations[b])
            .expect("never empty")
    });
    indices.reverse();

    drop(grad);

    for i in indices {
        x[i] = x[i].floor();
        let cost_floor: f64 = function(x.view());
        x[i] += 1.;
        let cost_ceiling: f64 = function(x.view());
        x[i] -= if cost_floor < cost_ceiling { 1. } else { 0. };
    }

    x.mapv(|x: f64| x as usize)
}

pub fn inertial_optimiser<T: Optimisable>(function: &mut T, start: ArrayView1<f64>) -> Results {
    let n = start.len();

    let mut x = start.to_owned();
    let mut c = function.call(x.view());

    let mut speed = Array::ones(n);
    // let mut cost_variations = grad(x.view());
    let mut cost_variations = Array1::zeros(x.len());

    let β = 0.94;
    let α = 0.05;
    let iter_max = 1_000;
    let mut n_iter = 0;
    let mut condition = true;
    let mut speed_norm: f64;

    let mut arg_min = start.to_owned();
    let mut min = function.call(start.view());

    while condition && (n_iter < iter_max) {
        n_iter += 1;

        python_interupt!(n_iter, 16);


        // print!("progress : {n_iter} / {iter_max}\r");

        // print!("{c} \r");

        // let β = 9;

        cost_variations = function.gradient(x.view());
        // println!("{:?}", cost_variations);
        speed = &speed * β - &cost_variations;
        x += &(&speed * α);
        // normaly useless
        // x.mapv_inplace(|d| if d < 0. {0.} else {d});

        speed_norm = l2_norm(speed.view());
        c = function.call(x.view());
        if function.should_record() {
            function.record(x.view(), c, Some(speed_norm));
        }
        if c < min {
            arg_min = x.clone();
            min = c;
        }

        condition = speed_norm > 1.;
    }

    let cost_variations = function.gradient(arg_min.view());

    let mut indices = (0..n).collect::<Vec<_>>();
    indices.sort_by(|&a, &b| {
        cost_variations[a]
            .partial_cmp(&cost_variations[b])
            .expect("never empty")
    });
    indices.reverse();

    for i in indices {
        arg_min[i] = arg_min[i].floor();
        let cost_floor: f64 = function.call(arg_min.view());
        arg_min[i] += 1.;
        let cost_ceiling: f64 = function.call(arg_min.view());
        arg_min[i] -= if cost_floor < cost_ceiling { 1. } else { 0. };
    }

    let arg_min = arg_min.mapv(|x: f64| x as usize);
    Results {
        argmin: arg_min.clone(),
        n_iter: n_iter,
        minimum: function.call(arg_min.mapv(|x: usize| x as f64).view()),
        convergence: function.dump_records(),
    }
}


pub fn simple_optimiser<T: FnMut(ArrayView1<f64>) -> f64>(
    function: &mut T,
    steps: ArrayView1<f64>,
    start: Array1<f64>,
) -> Results {
    let mut c = function(start.view());
    let n = start.len();
    let mut x = start.to_owned();

    // println!("{}", steps);


    let h: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 2]>> = Array2::from_diag(&steps);
    let mut b = true;
    let mut i = 0;
    let mut cost_variations = Vec::with_capacity(n + 1);
    
    while b {
        i += 1;
        // print!("iteration {i}\r");
        python_interupt!(i, 16);

        let mut g = &h + &x;
        cost_variations = g
            .map_axis_mut(Axis(1), |row| function(row.view()) - c)
            .to_vec();
        let (arg_min, _) = cost_variations.argminmax();
        // println!("{}", cost_variations[arg_min]);
        b = cost_variations[arg_min] < 0.;

        if b {
            x[arg_min] += steps[arg_min];
            c += cost_variations[arg_min];
        }
    }

    // println!("done in {i} iterations !");
    let argmin = rounding(function, x.view());
    Results {
        argmin: argmin.clone(),
        n_iter: i,
        minimum: function(argmin.mapv(|x: usize| x as f64).view()),
        convergence: Convergence::default()
    }
}

pub fn simple_optimiser_details<T: FnMut(ArrayView1<f64>) -> f64, F: FnMut(&mut Convergence, ArrayView1<f64>, f64)>(
    function: &mut T,
    steps: ArrayView1<f64>,
    start: Array1<f64>,
    record_function: &mut F
) -> Results {
    let mut c = function(start.view());
    let n = start.len();
    let mut x = start.to_owned();

    let mut returned_x = x.clone();
    // println!("{}", steps);


    let h: ArrayBase<ndarray::OwnedRepr<f64>, Dim<[usize; 2]>> = Array2::from_diag(&steps);
    let mut b = true;
    let mut i = 0;
    let mut cost_variations = Vec::with_capacity(n + 1);

    let mut convergence = Convergence::new();
    
    let mut j = 0;
    let mut above = 1;
    while j < above {
        // print!("iteration {i}\r");
        python_interupt!(i + j, 16);

        let mut g = &h + &x;
        cost_variations = g
            .map_axis_mut(Axis(1), |row| function(row.view()) - c)
            .to_vec();
        let (arg_min, _) = cost_variations.argminmax();
        b = cost_variations[arg_min] < 0.;

        if b {
            i += 1;
        } else {
            j += 1;
            if j == 1 {
                returned_x = x.clone();
                above = i / 2;
            }
        }

        x[arg_min] += steps[arg_min];
        c += cost_variations[arg_min];
        record_function(&mut convergence, x.view(), c);
    }

    let argmin = rounding(function, returned_x.view());
    Results {
        argmin: argmin.clone(),
        n_iter: i,
        minimum: function(argmin.mapv(|x: usize| x as f64).view()),
        convergence: convergence
    }
}



pub fn default_optimiser<T: Optimisable>(
    function: &mut T,
    steps: ArrayView1<f64>,
    start: ArrayView1<f64>,
) -> Results {
    let mut c = function.call(start.view());
    let n = start.len();
    let mut x = start.to_owned();



    let mut b = true;
    let mut i = 0;
    let mut cost_variations = Array1::zeros(x.len());
    while b {
        i += 1;
        // print!("iteration {i}\r");
        python_interupt!(i, 16);

        cost_variations = function.cost_variations(x.view()) - c;
        let arg_min = cost_variations
            .argmin()
            .expect("expect the costs variations to be non empty");
        b = cost_variations[arg_min] < 0.;

        if b {
            x[arg_min] += steps[arg_min];
            c += cost_variations[arg_min];
        }
    }

    // println!("done in {i} iterations !");

    let cost_variations = function.cost_variations(x.view()) - c;

    let mut indices = (0..n).collect::<Vec<_>>();
    indices.sort_by(|&a, &b| {
        cost_variations[a]
            .partial_cmp(&cost_variations[b])
            .expect("never empty")
    });
    indices.reverse();

    for i in indices {
        x[i] = x[i].floor();
        let cost_floor: f64 = function.call(x.view());
        x[i] += 1.;
        let cost_ceiling: f64 = function.call(x.view());
        x[i] -= if cost_floor < cost_ceiling { 1. } else { 0. };
    }

    let argmin = x.mapv(|x: f64| x as usize);

    Results {
        argmin: argmin.clone(),
        n_iter: i,
        minimum: function.call(argmin.mapv(|x: usize| x as f64).view()),
        convergence: function.dump_records(),
    }
}



pub fn default_optimiser_details<T: Optimisable>(
    function: &mut T,
    steps: ArrayView1<f64>,
    start: ArrayView1<f64>,
) -> Results {
    let mut c = function.call(start.view());
    let n = start.len();
    let mut x = start.to_owned();
    let mut xp = x.clone();
    let mut cp = c;

    let mut b = true;
    let mut i = 0;
    let mut cost_variations = Array1::zeros(x.len());
    let mut j = 0;
    let mut above = 1;
    while j < above {
        // print!("iteration {}\r", i + j);
        python_interupt!(i + j, 16);

        cost_variations = function.cost_variations(x.view()) - c;

        let arg_min = cost_variations
            .argmin()
            .expect("expect the costs varuations to be non empty");
        // println!("{}", cost_variations[arg_min]);
        b = cost_variations[arg_min] < 0.;

        if function.should_record() {
            function.record(x.view(), c, None);
        }

        if b {
            i += 1;
            x[arg_min] += steps[arg_min];
            c += cost_variations[arg_min];
            cp = c;
            xp = x.clone()
        } else {
            above = i / 2;
            j += 1;
            x[arg_min] += steps[arg_min];
            c += cost_variations[arg_min];
        }
    }

    // println!("done in {} iterations !", i + j);

    let cost_variations = function.cost_variations(xp.view()) - cp;

    let mut indices = (0..n).collect::<Vec<_>>();
    indices.sort_by(|&a, &b| {
        cost_variations[a]
            .partial_cmp(&cost_variations[b])
            .expect("never empty")
    });
    indices.reverse();

    for i in indices {
        xp[i] = xp[i].floor();
        let cost_floor: f64 = function.call(xp.view());
        xp[i] += 1.;
        let cost_ceiling: f64 = function.call(xp.view());
        xp[i] -= if cost_floor < cost_ceiling { 1. } else { 0. };
    }

    let argmin = xp.mapv(|z: f64| z as usize);

    Results {
        argmin: argmin.clone(),
        n_iter: i,
        minimum: function.call(argmin.mapv(|z: usize| z as f64).view()),
        convergence: function.dump_records(),
    }
}
