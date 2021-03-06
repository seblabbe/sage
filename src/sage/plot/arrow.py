"""
Arrows
"""
#*****************************************************************************
#       Copyright (C) 2006 Alex Clemesha <clemesha@gmail.com>,
#                          William Stein <wstein@gmail.com>,
#                     2008 Mike Hansen <mhansen@gmail.com>,
#                     2009 Emily Kirkman
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.plot.primitive import GraphicPrimitive
from sage.misc.decorators import options, rename_keyword
from sage.plot.colors import to_mpl_color

class CurveArrow(GraphicPrimitive):
    def __init__(self, path, options):
        """
        Returns an arrow graphics primitive along the provided path (bezier curve).

        EXAMPLES::

            sage: from sage.plot.arrow import CurveArrow
            sage: b = CurveArrow(path=[[(0,0),(.5,.5),(1,0)],[(.5,1),(0,0)]],options={})
            sage: b
            CurveArrow from (0, 0) to (0, 0)
        """
        import numpy as np
        self.path = path
        codes = [1] + (len(self.path[0])-1)*[len(self.path[0])]
        vertices = self.path[0]
        for curve in self.path[1:]:
            vertices += curve
            codes += (len(curve))*[len(curve)+1]
        self.codes = codes
        self.vertices = np.array(vertices, np.float)
        GraphicPrimitive.__init__(self, options)

    def get_minmax_data(self):
        """
        Returns a dictionary with the bounding box data.

        EXAMPLES::

            sage: from sage.plot.arrow import CurveArrow
            sage: b = CurveArrow(path=[[(0,0),(.5,.5),(1,0)],[(.5,1),(0,0)]],options={})
            sage: d = b.get_minmax_data()
            sage: d['xmin']
            0.0
            sage: d['xmax']
            1.0
        """
        return {'xmin': self.vertices[:,0].min(),
                'xmax': self.vertices[:,0].max(),
                'ymin': self.vertices[:,1].min(),
                'ymax': self.vertices[:,1].max()}

    def _allowed_options(self):
        """
        Return the dictionary of allowed options for the curve arrow graphics primitive.

        EXAMPLES::

             sage: from sage.plot.arrow import CurveArrow
             sage: list(sorted(CurveArrow(path=[[(0,0),(2,3)]],options={})._allowed_options().iteritems()))
             [('arrowsize', 'The size of the arrowhead'),
             ('arrowstyle', 'todo'),
             ('head', '2-d only: Which end of the path to draw the head (one of 0 (start), 1 (end) or 2 (both)'),
             ('hue', 'The color given as a hue.'),
             ('legend_label', 'The label for this item in the legend.'),
             ('linestyle', "2d only: The style of the line, which is one of 'dashed', 'dotted', 'solid', 'dashdot'."),
             ('rgbcolor', 'The color as an RGB tuple.'),
             ('width', 'The width of the shaft of the arrow, in points.'),
             ('zorder', '2-d only: The layer level in which to draw')]
        """
        return {'width':'The width of the shaft of the arrow, in points.',
                'rgbcolor':'The color as an RGB tuple.',
                'hue':'The color given as a hue.',
                'legend_label':'The label for this item in the legend.',
                'arrowstyle': 'todo',
                'linestyle': 'todo',
                'arrowsize':'The size of the arrowhead',
                'zorder':'2-d only: The layer level in which to draw',
                'head':'2-d only: Which end of the path to draw the head (one of 0 (start), 1 (end) or 2 (both)',
                'linestyle':"2d only: The style of the line, which is one of 'dashed', 'dotted', 'solid', 'dashdot'."}

    def _repr_(self):
        """
        Text representation of an arrow graphics primitive.

        EXAMPLES::

            sage: from sage.plot.arrow import CurveArrow
            sage: CurveArrow(path=[[(0,0),(1,4),(2,3)]],options={})._repr_()
            'CurveArrow from (0, 0) to (2, 3)'
        """
        return "CurveArrow from %s to %s"%(self.path[0][0],self.path[-1][-1])

    def _render_on_subplot(self, subplot):
        """
        Render this arrow in a subplot.  This is the key function that
        defines how this arrow graphics primitive is rendered in
        matplotlib's library.

        EXAMPLES::

        This function implicitly ends up rendering this arrow on a matplotlib subplot:
            sage: arrow(path=[[(0,1), (2,-1), (4,5)]])
        """
        options = self.options()
        width = float(options['width'])
        head = options.pop('head')
        if head == 0: style = '<|-'
        elif head == 1: style = '-|>'
        elif head == 2: style = '<|-|>'
        else: raise KeyError('head parameter must be one of 0 (start), 1 (end) or 2 (both).')
        arrowsize = float(options.get('arrowsize',5))
        head_width=arrowsize
        head_length=arrowsize*2.0
        color = to_mpl_color(options['rgbcolor'])
        from matplotlib.patches import FancyArrowPatch
        from matplotlib.path import Path
        bpath = Path(self.vertices, self.codes)
        p = FancyArrowPatch(path=bpath,
                            lw=width, arrowstyle='%s,head_width=%s,head_length=%s'%(style,head_width, head_length),
                            fc=color, ec=color, linestyle=options['linestyle'])
        p.set_zorder(options['zorder'])
        p.set_label(options['legend_label'])
        subplot.add_patch(p)
        return p


class Arrow(GraphicPrimitive):
    """
    Primitive class that initializes the (line) arrow graphics type

    EXAMPLES:

    We create an arrow graphics object, then take the 0th entry
    in it to get the actual Arrow graphics primitive::

        sage: P = arrow((0,1), (2,3))[0]
        sage: type(P)
        <class 'sage.plot.arrow.Arrow'>
        sage: P
        Arrow from (0.0,1.0) to (2.0,3.0)
    """
    def __init__(self, xtail, ytail, xhead, yhead, options):
        """
        Create an arrow graphics primitive.

        EXAMPLES::

            sage: from sage.plot.arrow import Arrow
            sage: Arrow(0,0,2,3,{})
            Arrow from (0.0,0.0) to (2.0,3.0)
        """
        self.xtail = float(xtail)
        self.xhead = float(xhead)
        self.ytail = float(ytail)
        self.yhead = float(yhead)
        GraphicPrimitive.__init__(self, options)

    def get_minmax_data(self):
        """
        Returns a bounding box for this arrow.

        EXAMPLES::

            sage: d = arrow((1,1), (5,5)).get_minmax_data()
            sage: d['xmin']
            1.0
            sage: d['xmax']
            5.0
        """
        return {'xmin': min(self.xtail, self.xhead),
                'xmax': max(self.xtail, self.xhead),
                'ymin': min(self.ytail, self.yhead),
                'ymax': max(self.ytail, self.yhead)}


    def _allowed_options(self):
        """
        Return the dictionary of allowed options for the line arrow graphics primitive.

        EXAMPLES::

             sage: from sage.plot.arrow import Arrow
             sage: list(sorted(Arrow(0,0,2,3,{})._allowed_options().iteritems()))
             [('arrowshorten', 'The length in points to shorten the arrow.'),
             ('arrowsize', 'The size of the arrowhead'),
             ('head', '2-d only: Which end of the path to draw the head (one of 0 (start), 1 (end) or 2 (both)'),
             ('hue', 'The color given as a hue.'),
             ('legend_label', 'The label for this item in the legend.'),
             ('linestyle', "2d only: The style of the line, which is one of 'dashed', 'dotted', 'solid', 'dashdot'."),
             ('rgbcolor', 'The color as an RGB tuple.'),
             ('width', 'The width of the shaft of the arrow, in points.'),
             ('zorder', '2-d only: The layer level in which to draw')]
        """
        return {'width':'The width of the shaft of the arrow, in points.',
                'rgbcolor':'The color as an RGB tuple.',
                'hue':'The color given as a hue.',
                'arrowshorten':'The length in points to shorten the arrow.',
                'arrowsize':'The size of the arrowhead',
                'legend_label':'The label for this item in the legend.',
                'zorder':'2-d only: The layer level in which to draw',
                'head':'2-d only: Which end of the path to draw the head (one of 0 (start), 1 (end) or 2 (both)',
                'linestyle':"2d only: The style of the line, which is one of 'dashed', 'dotted', 'solid', 'dashdot'."}

    def _plot3d_options(self, options=None):
        """
        Translate 2D plot options into 3D plot options.

        EXAMPLES::

            sage: P = arrow((0,1), (2,3), width=5)
            sage: p=P[0]; p
            Arrow from (0.0,1.0) to (2.0,3.0)
            sage: q=p.plot3d()
            sage: q.thickness
            5
        """
        if options == None:
            options = self.options()
        options = dict(self.options())
        options_3d = {}
        if 'width' in options:
            options_3d['thickness'] = options['width']
            del options['width']
        # ignore zorder and head in 3d plotting
        if 'zorder' in options:
            del options['zorder']
        if 'head' in options:
            del options['head']
        if 'linestyle' in options:
            del options['linestyle']
        options_3d.update(GraphicPrimitive._plot3d_options(self, options))
        return options_3d

    def plot3d(self, ztail=0, zhead=0, **kwds):
        """
        Takes 2D plot and places it in 3D.

        EXAMPLES::

            sage: A = arrow((0,0),(1,1))[0].plot3d()
            sage: A.jmol_repr(A.testing_render_params())[0]
            'draw line_1 diameter 2 arrow {0.0 0.0 0.0}  {1.0 1.0 0.0} '

        Note that we had to index the arrow to get the Arrow graphics
        primitive.  We can also change the height via the plot3d method
        of Graphics, but only as a whole::

            sage: A = arrow((0,0),(1,1)).plot3d(3)
            sage: A.jmol_repr(A.testing_render_params())[0][0]
            'draw line_1 diameter 2 arrow {0.0 0.0 3.0}  {1.0 1.0 3.0} '

        Optional arguments place both the head and tail outside the
        `xy`-plane, but at different heights.  This must be done on
        the graphics primitive obtained by indexing::

            sage: A=arrow((0,0),(1,1))[0].plot3d(3,4)
            sage: A.jmol_repr(A.testing_render_params())[0]
            'draw line_1 diameter 2 arrow {0.0 0.0 3.0}  {1.0 1.0 4.0} '
        """
        from sage.plot.plot3d.shapes2 import line3d
        options = self._plot3d_options()
        options.update(kwds)
        return line3d([(self.xtail, self.ytail, ztail), (self.xhead, self.yhead, zhead)], arrow_head=True, **options)

    def _repr_(self):
        """
        Text representation of an arrow graphics primitive.

        EXAMPLES::

            sage: from sage.plot.arrow import Arrow
            sage: Arrow(0,0,2,3,{})._repr_()
            'Arrow from (0.0,0.0) to (2.0,3.0)'
        """
        return "Arrow from (%s,%s) to (%s,%s)"%(self.xtail, self.ytail, self.xhead, self.yhead)

    def _render_on_subplot(self, subplot):
        """
        Render this arrow in a subplot.  This is the key function that
        defines how this arrow graphics primitive is rendered in
        matplotlib's library.

        EXAMPLES:

        This function implicitly ends up rendering this arrow on
        a matplotlib subplot::

            sage: arrow((0,1), (2,-1))

        TESTS:

        The length of the ends (shrinkA and shrinkB) should not depend
        on the width of the arrow, because Matplotlib already takes
        this into account. See :trac:`12836`::

            sage: fig = Graphics().matplotlib()
            sage: sp = fig.add_subplot(1,1,1)
            sage: a = arrow((0,0), (1,1))
            sage: b = arrow((0,0), (1,1), width=20)
            sage: p1 = a[0]._render_on_subplot(sp)
            sage: p2 = b[0]._render_on_subplot(sp)
            sage: p1.shrinkA == p2.shrinkA
            True
            sage: p1.shrinkB == p2.shrinkB
            True

        """
        options = self.options()
        head = options.pop('head')
        if head == 0: style = '<|-'
        elif head == 1: style = '-|>'
        elif head == 2: style = '<|-|>'
        else: raise KeyError('head parameter must be one of 0 (start), 1 (end) or 2 (both).')
        width = float(options['width'])
        arrowshorten_end = float(options.get('arrowshorten',0))/2.0
        arrowsize = float(options.get('arrowsize',5))
        head_width=arrowsize
        head_length=arrowsize*2.0
        color = to_mpl_color(options['rgbcolor'])
        from matplotlib.patches import FancyArrowPatch
        p = FancyArrowPatch((self.xtail, self.ytail), (self.xhead, self.yhead),
                            lw=width, arrowstyle='%s,head_width=%s,head_length=%s'%(style,head_width, head_length),
                            shrinkA=arrowshorten_end, shrinkB=arrowshorten_end,
                            fc=color, ec=color, linestyle=options['linestyle'])
        p.set_zorder(options['zorder'])
        p.set_label(options['legend_label'])
        subplot.add_patch(p)
        return p

def arrow(tailpoint=None, headpoint=None, **kwds):
    """
    Returns either a 2-dimensional or 3-dimensional arrow depending
    on value of points.

    For information regarding additional arguments, see either arrow2d?
    or arrow3d?.

    EXAMPLES::

        sage: arrow((0,0), (1,1))
        sage: arrow((0,0,1), (1,1,1))
    """
    try:
        return arrow2d(tailpoint, headpoint, **kwds)
    except ValueError:
        from sage.plot.plot3d.shapes import arrow3d
        return arrow3d(tailpoint, headpoint, **kwds)

@rename_keyword(color='rgbcolor')
@options(width=2, rgbcolor=(0,0,1),zorder=2, head = 1, linestyle='solid', legend_label=None)
def arrow2d(tailpoint=None, headpoint=None, path=None, **options):
    """
    If tailpoint and headpoint are provided, returns an arrow from (xmin, ymin)
    to (xmax, ymax).  If tailpoint or headpoint is None and path is not None,
    returns an arrow along the path.  (See further info on paths in bezier_path).

    INPUT:

    - ``tailpoint`` - the starting point of the arrow

    - ``headpoint`` - where the arrow is pointing to

    - ``path`` - the list of points and control points (see bezier_path for detail) that
      the arrow will follow from source to destination

    - ``head`` - 0, 1 or 2, whether to draw the head at the start (0), end (1) or both (2)
      of the path (using 0 will swap headpoint and tailpoint).  This is ignored
      in 3D plotting.

    - ``linestyle`` - The style of the line, which is one of 'dashed',
      'dotted', 'solid', 'dashdot', or '--', ':', '-', '-.', respectively.

    - ``width`` - (default: 2) the width of the arrow shaft, in points

    - ``color`` - (default: (0,0,1)) the color of the arrow (as an RGB tuple or a string)

    - ``hue`` - the color of the arrow (as a number)

    - ``arrowsize`` - the size of the arrowhead

    - ``arrowshorten`` - the length in points to shorten the arrow (ignored if using path
      parameter)

    - ``legend_label`` - the label for this item in the legend

    - ``zorder`` - the layer level to draw the arrow-- note that this is ignored in 3D
      plotting.

    EXAMPLES:

    A straight, blue arrow::

       sage: arrow2d((1, 1), (3, 3))

    Make a red arrow::

       sage: arrow2d((-1, -1), (2, 3), color=(1,0,0))
       sage: arrow2d((-1, -1), (2, 3), color='red')

    You can change the width of an arrow::

        sage: arrow2d((1, 1), (3, 3), width=5, arrowsize=15)

    Use a dashed line instead of a solid one for the arrow::

        sage: arrow2d((1, 1), (3, 3), linestyle='dashed')
        sage: arrow2d((1, 1), (3, 3), linestyle='--')

    A pretty circle of arrows::

        sage: sum([arrow2d((0,0), (cos(x),sin(x)), hue=x/(2*pi)) for x in [0..2*pi,step=0.1]])

    If we want to draw the arrow between objects, for example, the
    boundaries of two lines, we can use the arrowshorten option
    to make the arrow shorter by a certain number of points::

        sage: line([(0,0),(1,0)],thickness=10)+line([(0,1),(1,1)], thickness=10)+arrow2d((0.5,0),(0.5,1), arrowshorten=10,rgbcolor=(1,0,0))

    If BOTH headpoint and tailpoint are None, then an empty plot is returned::

        sage: arrow2d(headpoint=None, tailpoint=None)


    We can also draw an arrow with a legend::

        sage: arrow((0,0), (0,2), legend_label='up')

    Extra options will get passed on to show(), as long as they are valid::

        sage: arrow2d((-2, 2), (7,1), frame=True)
        sage: arrow2d((-2, 2), (7,1)).show(frame=True)
    """
    # Allow the usual linestyles used in the plot() command
    dict_line = {':': 'dotted', '-': 'solid', '--': 'dashed', '-.': 'dashdot'}
    if options['linestyle'] in dict_line:
        options['linestyle'] = dict_line[options['linestyle']]

    from sage.plot.all import Graphics
    g = Graphics()
    g._set_extra_kwds(Graphics._extract_kwds_for_show(options))

    if headpoint is not None and tailpoint is not None:
        xtail, ytail = tailpoint
        xhead, yhead = headpoint
        g.add_primitive(Arrow(xtail, ytail, xhead, yhead, options=options))
    elif path is not None:
        g.add_primitive(CurveArrow(path, options=options))
    elif tailpoint is None and headpoint is None:
        return g
    else:
        raise TypeError('Arrow requires either both headpoint and tailpoint or a path parameter.')
    if options['legend_label']:
        g.legend(True)
    return g
