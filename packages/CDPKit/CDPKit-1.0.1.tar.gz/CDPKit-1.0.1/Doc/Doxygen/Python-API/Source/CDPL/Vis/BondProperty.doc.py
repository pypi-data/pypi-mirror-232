#
# This file is part of the Chemical Data Processing Toolkit
#
# Copyright (C) Thomas Seidel <thomas.seidel@univie.ac.at>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; see the file COPYING. If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#

##
# \brief Provides keys for built-in Chem.Bond properties.
# 
class BondProperty(Boost.Python.instance):

    ##
    # \brief Specifies the color of the bond.
    # 
    # The color specified by this property takes precedence over the colors specified by Vis.ControlParameter.BOND_COLOR and Vis.MolecularGraphProperty.BOND_COLOR.
    # 
    # <b>Value Type:</b> Vis.Color
    # 
    COLOR = CDPL.Base.LookupKey(id=154, name='COLOR')

    ##
    # \brief Specifies the amount by which the non-central lines of asymmetric double bonds have to be trimmed at each line end.
    # 
    # The trim length can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the trim length will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the length grows/shrinks with the size of the chemical structure during viewport size adjustment. The trim length specified by this property takes precedence over the lengths specified by Vis.ControlParameter.DOUBLE_BOND_TRIM_LENGTH and Vis.MolecularGraphProperty.DOUBLE_BOND_TRIM_LENGTH. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    DOUBLE_BOND_TRIM_LENGTH = CDPL.Base.LookupKey(id=161, name='DOUBLE_BOND_TRIM_LENGTH')

    ##
    # \brief Specifies the font for bond labels.
    # 
    # The font specified by this property takes precedence over the fonts specified by Vis.ControlParameter.BOND_LABEL_FONT and Vis.MolecularGraphProperty.BOND_LABEL_FONT. <br>
    # 
    # <b>Value Type:</b> Vis.Font
    # 
    LABEL_FONT = CDPL.Base.LookupKey(id=163, name='LABEL_FONT')

    ##
    # \brief Specifies the margin of free space around bond labels.
    # 
    # The margin can either be specified as an absolute value or as a scaling factor for the primary label size given by Vis.ControlParameter.BOND_LABEL_SIZE, Vis.MolecularGraphProperty.BOND_LABEL_SIZE or Vis.BondProperty.LABEL_SIZE. If input-scaling is enabled, the width of the margin will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the margin will follow the size change of the chemical structure during viewport size adjustment. The margin specified by this property takes precedence over the margins specified by Vis.ControlParameter.BOND_LABEL_MARGIN and Vis.MolecularGraphProperty.BOND_LABEL_MARGIN. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    LABEL_MARGIN = CDPL.Base.LookupKey(id=165, name='LABEL_MARGIN')

    ##
    # \brief Specifies the size of bond labels.
    # 
    # The font size has to be specified as an absolute value. If input-scaling is enabled, the font size will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the font size will follow the size change of the chemical structure during viewport size adjustment. The font size specified by this property takes precedence over the sizes specified by Vis.ControlParameter.BOND_LABEL_SIZE and Vis.MolecularGraphProperty.BOND_LABEL_SIZE. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    LABEL_SIZE = CDPL.Base.LookupKey(id=164, name='LABEL_SIZE')

    ##
    # \brief Specifies the distance between the lines of double and triple bonds.
    # 
    # The distance can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the line distance will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the distance grows/shrinks with the size of the chemical structure during viewport size adjustment. The line spacing specified by this property takes precedence over the distances specified by Vis.ControlParameter.BOND_LINE_SPACING and Vis.MolecularGraphProperty.BOND_LINE_SPACING. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    LINE_SPACING = CDPL.Base.LookupKey(id=156, name='LINE_SPACING')

    ##
    # \brief Specifies the width of bond lines.
    # 
    # The width can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the line width will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the line width grows/shrinks with the size of the chemical structure during viewport size adjustment. The line width specified by this property takes precedence over the widths specified by Vis.ControlParameter.BOND_LINE_WIDTH and Vis.MolecularGraphProperty.BOND_LINE_WIDTH.
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    LINE_WIDTH = CDPL.Base.LookupKey(id=155, name='LINE_WIDTH')

    ##
    # \brief Specifies the length of the lines in reaction center marks.
    # 
    # The length can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the line length will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the length grows/shrinks with the size of the chemical structure during viewport size adjustment. The line length specified by this property takes precedence over the length specified by Vis.ControlParameter.REACTION_CENTER_LINE_LENGTH or Vis.MolecularGraphProperty.REACTION_CENTER_LINE_LENGTH. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification \see Vis.ControlParameter.SHOW_BOND_REACTION_INFOS
    # 
    REACTION_CENTER_LINE_LENGTH = CDPL.Base.LookupKey(id=159, name='REACTION_CENTER_LINE_LENGTH')

    ##
    # \brief Specifies the distance between the lines in reaction center marks.
    # 
    # The distance can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the line distance will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the distance grows/shrinks with the size of the chemical structure during viewport size adjustment. The line spacing specified by this property takes precedence over the spacing specified by Vis.ControlParameter.REACTION_CENTER_LINE_SPACING or Vis.MolecularGraphProperty.REACTION_CENTER_LINE_SPACING. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification \see Vis.ControlParameter.SHOW_BOND_REACTION_INFOS
    # 
    REACTION_CENTER_LINE_SPACING = CDPL.Base.LookupKey(id=160, name='REACTION_CENTER_LINE_SPACING')

    ##
    # \brief Specifies the amount by which the non-central lines of triple bonds have to be trimmed at each line end.
    # 
    # The trim length can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the trim length will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the length grows/shrinks with the size of the chemical structure during viewport size adjustment. The trim length specified by this property takes precedence over the lengths specified by Vis.ControlParameter.TRIPLE_BOND_TRIM_LENGTH and Vis.MolecularGraphProperty.TRIPLE_BOND_TRIM_LENGTH. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    TRIPLE_BOND_TRIM_LENGTH = CDPL.Base.LookupKey(id=162, name='TRIPLE_BOND_TRIM_LENGTH')

    ##
    # \brief Specifies the distance between the hashes of down stereo bonds.
    # 
    # The distance can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the hash distance will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the hash distance grows/shrinks with the size of the chemical structure during viewport size adjustment. The hash spacing specified by this property takes precedence over the distances specified by Vis.ControlParameter.STEREO_BOND_HASH_SPACING and Vis.MolecularGraphProperty.STEREO_BOND_HASH_SPACING. <br>
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    STEREO_BOND_HASH_SPACING = CDPL.Base.LookupKey(id=158, name='STEREO_BOND_HASH_SPACING')

    ##
    # \brief Specifies the width of wedge-shaped stereo bonds.
    # 
    # The width can either be specified as an absolute value or as a scaling factor for the bond length. If input-scaling is enabled, the wedge width will follow the size change of the chemical structure during bond length normalization. If output-scaling is enabled, the wedge width grows/shrinks with the size of the chemical structure during viewport size adjustment. The wedge width specified by this property takes precedence over the width specified by Vis.ControlParameter.STEREO_BOND_WEDGE_WIDTH or Vis.MolecularGraphProperty.STEREO_BOND_WEDGE_WIDTH.
    # 
    # <b>Value Type:</b> Vis.SizeSpecification
    # 
    STEREO_BOND_WEDGE_WIDTH = CDPL.Base.LookupKey(id=157, name='STEREO_BOND_WEDGE_WIDTH')
