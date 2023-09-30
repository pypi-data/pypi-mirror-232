# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import os
#%%

def logo(kind='print'):
    """
    Load Envidan logo for use in for example a Matplotlib figure
    
    Use:
        Put logon in Matplotlib figures by adding an axes.
        
        logo = logo()
        ax_logo = fig.add_axes([0.80,0.94,0.16,0.20], anchor='NE', zorder=-1)
        ax_logo.imshow(logo)
        ax_logo.axis('off')

    Parameters
    ----------
    kind : str, optional
        Kind of logo to load. Options are "print" and "web". The default is 'print'.

    Returns
    -------
    logo : Array of uint8
        Array of uint8 number representing the image.

    """
    
    module_dir = os.path.dirname(__file__)

    if kind == 'print':
        file_path = os.path.join(module_dir, 'ed_logo_blue_print.jpg')
        logo = plt.imread(file_path)
    elif kind == 'web':
        file_path = os.path.join(module_dir, 'ed_logo_blue_web.png')
        logo = plt.imread(file_path)
    else:
        raise NameError(f'{kind} is unknown')
    return logo

