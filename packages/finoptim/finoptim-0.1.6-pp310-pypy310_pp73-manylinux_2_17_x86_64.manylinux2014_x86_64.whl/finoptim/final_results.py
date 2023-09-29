import pandas as pd

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class FinalResults:
    """Class for keeping tidy results

    Returns:
        FinalResults: An object holding a `pd.DataFrame` with optimal commitments and able to pretty print it
    """
    optimal_arangment: pd.DataFrame
    minimum: float
    coverage: float
    underutilization_cost: float
    n_iter: int = 0
    step_size: Optional[float] = None
    convergence: Optional[List[float]] = None
    formatted: Optional[pd.DataFrame] = None

    def format(self, name_dict: Optional[dict] = None, **kwargs: List[dict]) -> pd.DataFrame:
        """
        ## YOU HAVE TO GIVE NAMED ARGUMENTS !

        The name of your argument will be the name of the added column.

        Create a new `DataFrame` out of `self.optimal_arangment` with prettier values.
        It is sorted by price, and you can add any columns you want using a dictionnary mapping
        the *guid*s to your wanted values

        Returns:
            pd.DataFrame: prettier DataFrame

        Examples
        --------
        ```python
        res = fp.optimise(df_real, prices_df)
        guid_to_instance_name = {"K7YHHNFGTNN2DP28" : 'i3.large', 'SAHHHV5TXVX4DCTS' : 'r5.large'}
        res.format(instance_type=guid_to_instance_name)
        print(res)
        >>>
        ╭─────────────────┬──────────────────────────┬───────────────╮
        │ instance_type   │  three_year_commitments  │  price_per_D  │
        ├─────────────────┼──────────────────────────┼───────────────┤
        │ i3.large        │           1338           │     2,886     │
        │ r5.large        │           1570           │     2,564     │
        │ savings plans   │           1937           │     1,937     │
        ╰─────────────────┴──────────────────────────┴───────────────╯
        ```
        """
        res = self.optimal_arangment
        price_col, rest = res.columns[-1], res.columns[:-1]
        md = res.loc[res[price_col] != 0].drop_duplicates(
        ).sort_values(by=price_col, ascending=False)

        # for k, mapping in name_dict.items():
        #     md[k] = md.index.map(mapping)
        # md = md[list(kwargs) + list(rest) + [price_col]]

        for k, mapping in kwargs.items():
            md[k] = md.index.map(mapping)
        md = md[list(kwargs) + list(rest) + [price_col]]
        self.formatted = md
        return md

    def plot(self, usage: pd.DataFrame, top: float = 0., **kwargs):
        """A quick helper to plot your results.

        You probably don't want to use this code as is, but I hope it can inspire you.

        Args:
            usage (pd.DataFrame): the same usage you used for the optimisation
            top (float): You can filter instances you want to plot by their usage sum, and only keep the top quantile.

        Returns:
            I don't even know: some matplotlib stuff to display the plot, I guess
        """
        from matplotlib import pyplot
        import seaborn as sns

        sums = usage.sum()
        c = usage.loc[:, sums > sums.quantile(top)].columns
        j = usage.loc[:, c]
        j = j.loc[~j.isna().any(axis=1), :]

        k = pd.melt(j, ignore_index=False, var_name="guid", value_name='usage').reset_index()

        k['type'] = 'usage'
        tmp = pd.DataFrame({
            'date' : k['date'],
            'guid' : k.guid,
            'usage' : k.guid.map(self.optimal_arangment['three_years_commitments']),
            'type' : 'reserved instances'})

        k = pd.concat([k, tmp], ignore_index=True)
        # k['name'] = k.guid.map(name_dict).str.split('.', expand=True)[0] + ' ' + k.guid.map(region_dict)

        a4_dims = (11.7, 8.27)
        fig, ax = pyplot.subplots(figsize=a4_dims)

        sns.lineplot(data=k,
                    ax=ax,
                    x='date',
                    y='usage',
                    hue='guid',
                    style='type')
        ax.grid(linestyle = '--', linewidth = 0.2)
        if 'title' in kwargs.keys():
            ax.set_title(kwargs.get("title"))
        if 'ylabel' in kwargs.keys():
            ax.set_ylabel(kwargs.get("ylabel"))
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

        return fig, ax

    def __repr__(self) -> str:
        if self.formatted is None:
            return f"minimum : {self.minimum:_.0f}, coverage : {self.coverage*100:.1f} %"
        return self.formatted.to_markdown(index=False, tablefmt='rounded_outline', floatfmt=',.0f')
