from mplex import core


def add_text(
    x,
    y,
    s,
    pad=0,
    transform="axes",
    pad_unit="offset points",
    ha="l",
    va="b",
    outline_kwargs=None,
    ax=None,
    **kwargs,
):
    import matplotlib.pyplot as plt

    from mplex.utils import safe_unpack

    pad = safe_unpack(pad)

    if ax is None:
        ax = plt.gca()

    if isinstance(transform, str):
        transform = transform.strip().lower()[0]
        transform = dict(
            d=ax.transData,
            x=ax.get_xaxis_transform(),
            y=ax.get_yaxis_transform(),
        ).get(transform, ax.transAxes)

    if len(ha) == 1:
        ha = core.get_ha(ha)

    if len(va) == 1:
        va = core.get_va(va)

    text = ax.annotate(s, (x, y), pad, transform, pad_unit, ha=ha, va=va, **kwargs)

    if outline_kwargs is not None:
        from matplotlib import patheffects

        text.set_path_effects(
            [patheffects.Stroke(**outline_kwargs), patheffects.Normal()]
        )

    return text
