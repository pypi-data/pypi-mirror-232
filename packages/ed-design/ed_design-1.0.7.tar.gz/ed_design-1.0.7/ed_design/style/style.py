# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import ed_design as edd
import os
import pkg_resources

# %%


def style(style='envidan', prop_cycle_palette='normal', cycle_repeat=10):
    """
    Sets matplotlib style with relevant stylesheet file (mpl)

    Parameters
    ----------
    style : str, optional
        Style name. The default is 'envidan'.
    prop_cycle_palette : str, optional
        Color palette to use as default prop_cycle. The default is 'normal'.
    cycle_repeat : int, optional
        N times to repeat the color palette in case plot has need for more colors
        Matplotlib will revert to another palette if not enough colors

    Returns
    -------
    None.

    """

    # module_dir = os.path.dirname(__file__)

    if style == 'envidan':
        try:
            file_path = pkg_resources.resource_filename(
                __name__, '/envidan.mplstyle')
            plt.style.use(file_path)
            prop_cycle(prop_cycle_palette, cycle_repeat)
        except FileNotFoundError:
            print(
                "The 'envidan.mplstyle' file was not found. Check your package structure.")

    if style == 'default':
        plt.style.use('default')

    # TODO Include Segoe UI font int his somehow
    return None


def prop_cycle(palette='normal', cycle_repeat=10):
    """
    Sets the color prop_cycle in Matplotlib. The palette name must be a valid
    palette from ed_design.Colors().get_palette(palette)

    Parameters
    ----------
    palette : str, optional
        Color prop cycle name. The default is 'normal'.
    cycle_repeat : int, optional
        N times to repeat the color palette in case plot has need for more colors
        Matplotlib will revert to another palette if not enough colors

    Returns
    -------
    None.

    """
    colors = edd.Colors()
    prop_cycle_palette = colors.get_palette(palette) * cycle_repeat
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=prop_cycle_palette)
    return None


def font_check(font_name=None):
    """
    Checks for system installed fonts Sathoshi and Segoe UI.
    Can also check for any other font name.

    Parameters
    ----------
    font_name : str, optional
        Font name to check for. The default is None.

    Returns
    -------
    None.

    """
    available_fonts = fm.findSystemFonts(fontpaths=None, fontext='otf')

    font_names_satoshi = [
        'Satoshi-Regular',
        'Satoshi-Black',
        'Satoshi-BlackItalic',
        'Satoshi-Bold',
        'Satoshi-BoldItalic',
        'Satoshi-Italic',
        'Satoshi-Light',
        'Satoshi-LightItalic',
        'Satoshi-Medium',
        'Satoshi-MediumItalic',
    ]

    font_names_segoe_ui = [
        'Segoe UI Bold Italic',
        'Segoe UI Bold',
        'Segoe UI Italic',
        'Segoe UI',
    ]

    if font_name is None:
        satoshi_lst = []
        for font in font_names_satoshi:
            if not any(font in font_path for font_path in available_fonts):
                satoshi_lst.append(font)
        if len(satoshi_lst) == 0:
            pass
        else:
            print(
                f'The fonts {satoshi_lst}" are not present on your system. Please install them from the path ed_design/style/_fonts/_satoshi')

        # The Segoe UI font messes up Maconomy so dont install this font !!
        # segoe_ui_lst = []
        # for font in font_names_segoe_ui:
        #     if not any(font in font_path for font_path in available_fonts):
        #         segoe_ui_lst.append(font)
        # if len(segoe_ui_lst) == 0:
        #     pass
        # else:
        #     print(f'The fonts {segoe_ui_lst}" are not present on your system. Please install them from the path ed_design/style/_fonts/_segoe_ui')

    if font_name is not None:
        if not any(font_name in font_path for font_path in available_fonts):
            print(f'The "{font_name}" font is not present on your system')
    return
