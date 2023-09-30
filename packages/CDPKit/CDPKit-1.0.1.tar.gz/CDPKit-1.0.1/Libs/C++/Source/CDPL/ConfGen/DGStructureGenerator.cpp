/* 
 * DGStructureGenerator.cpp 
 *
 * This file is part of the Chemical Data Processing Toolkit
 *
 * Copyright (C) 2003 Thomas Seidel <thomas.seidel@univie.ac.at>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library; see the file COPYING. If not, write to
 * the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

 
#include "StaticInit.hpp"

#include <boost/random/uniform_real.hpp>

#include "CDPL/ConfGen/DGStructureGenerator.hpp"
#include "CDPL/Chem/MolecularGraph.hpp"
#include "CDPL/Chem/AtomFunctions.hpp"
#include "CDPL/Chem/BondFunctions.hpp"


using namespace CDPL;


ConfGen::DGStructureGenerator::DGStructureGenerator(): 
    molGraph(0), settings(DGStructureGeneratorSettings::DEFAULT)
{
    phase1CoordsGen.setNumCycles(70);
    phase1CoordsGen.setCycleStepCountFactor(1.3);
    phase1CoordsGen.setStartLearningRate(1.0);
    phase1CoordsGen.setLearningRateDecrement(0.9 / 70);
}

ConfGen::DGStructureGeneratorSettings& ConfGen::DGStructureGenerator::getSettings()
{
    return settings;
}

const ConfGen::DGStructureGeneratorSettings& ConfGen::DGStructureGenerator::getSettings() const
{
    return settings;
}

const Util::BitSet& ConfGen::DGStructureGenerator::getExcludedHydrogenMask() const
{
    return dgConstraintsGen.getExcludedHydrogenMask();
}

void ConfGen::DGStructureGenerator::setup(const Chem::MolecularGraph& molgraph, 
                                          const ForceField::MMFF94InteractionData& ia_data)
{
    setup(molgraph, &ia_data);
}

void ConfGen::DGStructureGenerator::setup(const Chem::MolecularGraph& molgraph) 
{
    setup(molgraph, 0);
}

std::size_t ConfGen::DGStructureGenerator::getNumAtomStereoCenters() const
{
    return dgConstraintsGen.getNumAtomStereoCenters();
}

std::size_t ConfGen::DGStructureGenerator::getNumBondStereoCenters() const
{
    return dgConstraintsGen.getNumBondStereoCenters();
}

bool ConfGen::DGStructureGenerator::generate(Math::Vector3DArray& coords)
{
    if (!molGraph)
        return false;

    std::size_t num_atoms = molGraph->getNumAtoms();
    const Util::BitSet& x_h_mask = dgConstraintsGen.getExcludedHydrogenMask();

    coords.resize(num_atoms);

    boost::random::uniform_real_distribution<double> coord_dist(-settings.getBoxSize() * 0.5, settings.getBoxSize() * 0.5);

    for (std::size_t i = 0; i < num_atoms; i++) {
        if (x_h_mask.test(i))
            continue;
        
        Math::Vector3D::Pointer pos = coords[i].getData();

        pos[0] = coord_dist(randomEngine);
        pos[1] = coord_dist(randomEngine);
        pos[2] = coord_dist(randomEngine);
    }

    phase1CoordsGen.generate(molGraph->getNumAtoms(), coords.getData());

    if (settings.enablePlanarityConstraints()) 
        phase2CoordsGen.generate(molGraph->getNumAtoms(), coords.getData());
    
    if (settings.regardAtomConfiguration() && !checkAtomConfigurations(coords))
        return false;

    if (settings.regardBondConfiguration() && !checkBondConfigurations(coords))
        return false;

    return true;
}

void ConfGen::DGStructureGenerator::setup(const Chem::MolecularGraph& molgraph, 
                                          const ForceField::MMFF94InteractionData* ia_data)
{
    molGraph = &molgraph;
    dgConstraintsGen.getSettings() = settings;

    if (ia_data)
        dgConstraintsGen.setup(molgraph, *ia_data);
    else
        dgConstraintsGen.setup(molgraph);

    phase1CoordsGen.clearDistanceConstraints();
    phase1CoordsGen.clearVolumeConstraints();
    phase1CoordsGen.setRandomSeed(170375);

    dgConstraintsGen.addBondLengthConstraints(phase1CoordsGen);
    dgConstraintsGen.addBondAngleConstraints(phase1CoordsGen);
    dgConstraintsGen.addBondConfigurationConstraints(phase1CoordsGen);
    dgConstraintsGen.add14DistanceConstraints(phase1CoordsGen);
    dgConstraintsGen.addDefaultDistanceConstraints(phase1CoordsGen);
    dgConstraintsGen.addAtomConfigurationConstraints(phase1CoordsGen);
    
    phase1CoordsGen.orderDistanceConstraints();

    if (settings.enablePlanarityConstraints()) {
        phase2CoordsGen = phase1CoordsGen;

        dgConstraintsGen.addAtomPlanarityConstraints(phase2CoordsGen);     
        dgConstraintsGen.addBondPlanarityConstraints(phase2CoordsGen);

    } else {
        phase2CoordsGen.clearVolumeConstraints();
        phase2CoordsGen.clearDistanceConstraints();
    }

    randomEngine.seed(170375);
}

bool ConfGen::DGStructureGenerator::checkAtomConfigurations(Math::Vector3DArray& coords) const
{
    using namespace Chem;

    for (DGConstraintGenerator::ConstStereoCenterDataIterator it = dgConstraintsGen.getAtomStereoCenterDataBegin(),
             end = dgConstraintsGen.getAtomStereoCenterDataEnd(); it != end; ++it) {

        const DGConstraintGenerator::StereoCenterData& sc_data = *it;

        if (calcAtomConfiguration(molGraph->getAtom(sc_data.first), *molGraph, sc_data.second, coords) != sc_data.second.getConfiguration()) 
            return false;
    }

    return true;
}

bool ConfGen::DGStructureGenerator::checkBondConfigurations(Math::Vector3DArray& coords) const
{
    for (DGConstraintGenerator::ConstStereoCenterDataIterator it = dgConstraintsGen.getBondStereoCenterDataBegin(),
             end = dgConstraintsGen.getBondStereoCenterDataEnd(); it != end; ++it) {

        const DGConstraintGenerator::StereoCenterData& sc_data = *it;

        if (calcBondConfiguration(molGraph->getBond(sc_data.first), *molGraph, sc_data.second, coords) != sc_data.second.getConfiguration())
            return false;
    }

    return true;
}

const ConfGen::DGConstraintGenerator& ConfGen::DGStructureGenerator::getConstraintGenerator() const
{
    return dgConstraintsGen;
}
