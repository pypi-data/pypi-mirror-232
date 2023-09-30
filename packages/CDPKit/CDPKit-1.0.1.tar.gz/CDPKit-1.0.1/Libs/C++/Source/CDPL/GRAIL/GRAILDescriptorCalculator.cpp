/* 
 * GRAILDescriptorCalculator.cpp 
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

#include <iterator>
#include <algorithm>
#include <cmath>
#include <mutex>

#include "CDPL/GRAIL/GRAILDescriptorCalculator.hpp"
#include "CDPL/GRAIL/FeatureFunctions.hpp"
#include "CDPL/GRAIL/FeatureType.hpp"
#include "CDPL/Chem/Atom.hpp"
#include "CDPL/Chem/AtomFunctions.hpp"
#include "CDPL/Chem/Entity3DFunctions.hpp"
#include "CDPL/Chem/AtomType.hpp"
#include "CDPL/Pharm/HydrophobicAtomFeatureGenerator.hpp"
#include "CDPL/Pharm/FeatureFunctions.hpp"
#include "CDPL/Pharm/HBondingInteractionScore.hpp"
#include "CDPL/Pharm/XBondingInteractionScore.hpp"
#include "CDPL/Pharm/CationPiInteractionScore.hpp"
#include "CDPL/Pharm/HydrophobicInteractionScore.hpp"
#include "CDPL/Pharm/FeatureInteractionScoreCombiner.hpp"
#include "CDPL/Pharm/ParallelPiPiInteractionScore.hpp"
#include "CDPL/Pharm/OrthogonalPiPiInteractionScore.hpp"
#include "CDPL/ForceField/AtomFunctions.hpp"
#include "CDPL/ForceField/UtilityFunctions.hpp"
#include "CDPL/ForceField/UFFAtomTypePropertyTable.hpp"
#include "CDPL/MolProp/AtomFunctions.hpp"
#include "CDPL/MolProp/AtomContainerFunctions.hpp"
#include "CDPL/MolProp/MolecularGraphFunctions.hpp"
#include "CDPL/Base/Exceptions.hpp"
#include "CDPL/Internal/Octree.hpp"


using namespace CDPL;


namespace
{

    struct FtrInteractionFuncData
    {

        typedef Pharm::FeatureInteractionScore::SharedPointer ScoringFuncPtr;
        
        unsigned int   ligFtrType;
        unsigned int   tgtFtrType;
        ScoringFuncPtr scoringFunc;
    };

    typedef std::vector<FtrInteractionFuncData> FtrInteractionFuncList;

    FtrInteractionFuncList ftrInteractionFuncList;
    std::once_flag initFtrInteractionFuncListFlag;
    
    void initFtrInteractionFuncList()
    {
        using namespace Pharm;

        typedef FeatureInteractionScore::SharedPointer FISPtr;
        
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::POSITIVE_IONIZABLE, GRAIL::FeatureType::AROMATIC, FISPtr(new CationPiInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::AROMATIC, GRAIL::FeatureType::POSITIVE_IONIZABLE, FISPtr(new CationPiInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::HYDROPHOBIC, GRAIL::FeatureType::HYDROPHOBIC, FISPtr(new HydrophobicInteractionScore()) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::AROMATIC, GRAIL::FeatureType::AROMATIC,
                  FISPtr(new FeatureInteractionScoreCombiner(FISPtr(new OrthogonalPiPiInteractionScore()), FISPtr(new ParallelPiPiInteractionScore()))) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N3, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N3, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N3, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N2, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N2, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N2, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });
                      
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Nar, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Nar, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Nar, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Nam, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Nam, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Nam, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Npl3, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Npl3, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_Npl3, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N4, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N4, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_N4, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });
                
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_O3, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_O3, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_O3, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_S3, GRAIL::FeatureType::H_BOND_ACCEPTOR_N, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_S3, GRAIL::FeatureType::H_BOND_ACCEPTOR_O, FISPtr(new HBondingInteractionScore(true)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_DONOR_S3, GRAIL::FeatureType::H_BOND_ACCEPTOR_S, FISPtr(new HBondingInteractionScore(true)) });

        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                      
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N3, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N3, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N3, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                       
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N2, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N2, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N2, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                        
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N1, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N1, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_N1, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                      
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Nar, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Nar, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Nar, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                        
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Npl3, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Npl3, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Npl3, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                      
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_O3, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_O3, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_O3, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                     
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_O2, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_O2, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_O2, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                    
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Oco2, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Oco2, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_Oco2, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                    
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_S3, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_S3, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_S3, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                       
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_S2, GRAIL::FeatureType::H_BOND_DONOR_N, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_S2, GRAIL::FeatureType::H_BOND_DONOR_O, FISPtr(new HBondingInteractionScore(false)) });
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::H_BOND_ACCEPTOR_S2, GRAIL::FeatureType::H_BOND_DONOR_S, FISPtr(new HBondingInteractionScore(false)) });
                     
        ftrInteractionFuncList.push_back({ GRAIL::FeatureType::HALOGEN_BOND_DONOR, GRAIL::FeatureType::HALOGEN_BOND_ACCEPTOR, FISPtr(new XBondingInteractionScore(true)) });
    }

    struct LigandFtrType
    {

        unsigned int type;
        bool         isHBD;

    } LIGAND_DESCR_FTR_TYPES[] = {
        { GRAIL::FeatureType::POSITIVE_IONIZABLE, false },
        { GRAIL::FeatureType::NEGATIVE_IONIZABLE, false },
        { GRAIL::FeatureType::AROMATIC, false },
        { GRAIL::FeatureType::HYDROPHOBIC, false },
        { GRAIL::FeatureType::H_BOND_DONOR, true },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR, false },
        { GRAIL::FeatureType::HALOGEN_BOND_DONOR, false },
        { GRAIL::FeatureType::HALOGEN_BOND_ACCEPTOR, false },
        { GRAIL::FeatureType::H_BOND_DONOR_N3, true },
        { GRAIL::FeatureType::H_BOND_DONOR_N2, true },
        { GRAIL::FeatureType::H_BOND_DONOR_Nar, true },
        { GRAIL::FeatureType::H_BOND_DONOR_Nam, true },
        { GRAIL::FeatureType::H_BOND_DONOR_Npl3, true },
        { GRAIL::FeatureType::H_BOND_DONOR_N4, true },
        { GRAIL::FeatureType::H_BOND_DONOR_O3, true },
        { GRAIL::FeatureType::H_BOND_DONOR_S3, true },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_N3, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_N2, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_N1, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_Nar, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_Npl3, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_O3, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_O2, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_Oco2, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_S3, false },
        { GRAIL::FeatureType::H_BOND_ACCEPTOR_S2, false }
    };

    const double HYDROPHOBICIY_THRESHOLD         = 0.15;
    const double FEATURE_DISTANCE_CUTOFF         = 10.0;
    const double ESTAT_DISTANCE_CUTOFF           = 20.0;
    const double DIELECTRIC_CONST                = 1.0;
    const double VDW_DISTANCE_CUTOFF             = 10.0;
    const double VDW_POLAR_H_DIST_SCALING_FACTOR = 0.5;
}


constexpr std::size_t GRAIL::GRAILDescriptorCalculator::TOTAL_DESCRIPTOR_SIZE;
constexpr std::size_t GRAIL::GRAILDescriptorCalculator::LIGAND_DESCRIPTOR_SIZE;


GRAIL::GRAILDescriptorCalculator::GRAILDescriptorCalculator():
    tgtPharmGenerator(Pharm::DefaultPharmacophoreGenerator::STATIC_H_DONORS | Pharm::DefaultPharmacophoreGenerator::PI_NI_ON_CHARGED_GROUPS_ONLY),
    tgtAtomOctree(new Octree()), tgtFtrSubsets(FeatureType::MAX_EXT_TYPE + 1),
    ligPharmGenerator(Pharm::DefaultPharmacophoreGenerator::PI_NI_ON_CHARGED_GROUPS_ONLY), ligFtrSubsets(FeatureType::MAX_EXT_TYPE + 1),
    numLigAtoms(0)
{
    initPharmGenerators();
}

GRAIL::GRAILDescriptorCalculator::GRAILDescriptorCalculator(const GRAILDescriptorCalculator& calc):
    tgtPharmGenerator(Pharm::DefaultPharmacophoreGenerator::STATIC_H_DONORS | Pharm::DefaultPharmacophoreGenerator::PI_NI_ON_CHARGED_GROUPS_ONLY),
    tgtPharmacophore(calc.tgtPharmacophore), tgtAtomCharges(calc.tgtAtomCharges), tgtAtomVdWParams(calc.tgtAtomVdWParams),
    tgtAtomCoords(calc.tgtAtomCoords), tgtAtomOctree(new Octree()), tgtFtrSubsets(FeatureType::MAX_EXT_TYPE + 1),
    ligPharmGenerator(Pharm::DefaultPharmacophoreGenerator::PI_NI_ON_CHARGED_GROUPS_ONLY), ligAtomCharges(calc.ligAtomCharges),
    ligAtomVdWParams(calc.ligAtomVdWParams), ligHeavyAtoms(calc.ligHeavyAtoms), ligFtrSubsets(calc.ligFtrSubsets),
    ligFtrAtoms(calc.ligFtrAtoms), ligFtrWeights(calc.ligFtrWeights), numLigAtoms(calc.numLigAtoms)
{
    initPharmGenerators();

    tgtAtomOctree->initialize(tgtAtomCoords);

    copyTgtFtrSubsets(calc.tgtFtrSubsets);

    std::copy(calc.ligDescriptor, calc.ligDescriptor + LIGAND_DESCRIPTOR_SIZE, ligDescriptor);
}

GRAIL::GRAILDescriptorCalculator& GRAIL::GRAILDescriptorCalculator::operator=(const GRAILDescriptorCalculator& calc)
{
    if (this == &calc)
        return *this;

    ligFtrSubsets = calc.ligFtrSubsets;
    ligFtrAtoms = calc.ligFtrAtoms;
    ligFtrWeights = calc.ligFtrWeights;
    ligHeavyAtoms = calc.ligHeavyAtoms;
    ligAtomCharges = calc.ligAtomCharges;
    ligAtomVdWParams = calc.ligAtomVdWParams;
    numLigAtoms = calc.numLigAtoms;
    tgtAtomCharges = calc.tgtAtomCharges;
    tgtAtomVdWParams = calc.tgtAtomVdWParams;
    tgtAtomCoords = calc.tgtAtomCoords;
    tgtPharmacophore = calc.tgtPharmacophore;

    tgtAtomOctree->initialize(tgtAtomCoords);

    copyTgtFtrSubsets(calc.tgtFtrSubsets);

    std::copy(calc.ligDescriptor, calc.ligDescriptor + LIGAND_DESCRIPTOR_SIZE, ligDescriptor);
    
    return *this;
}

void GRAIL::GRAILDescriptorCalculator::initTargetData(const Chem::MolecularGraph& tgt_env, const Chem::Atom3DCoordinatesFunction& coords_func, bool tgt_env_changed)
{
    using namespace Pharm;

    std::size_t num_atoms = tgt_env.getNumAtoms();

    tgtAtomCoords.resize(num_atoms);

    if (tgt_env_changed) {
        if (tgtAtomCharges.size() < num_atoms)
            tgtAtomCharges.resize(num_atoms);

        if (tgtAtomVdWParams.size() < num_atoms)
            tgtAtomVdWParams.resize(num_atoms);
    }
    
    for (std::size_t i = 0; i < num_atoms; i++) {
        const Chem::Atom& atom = tgt_env.getAtom(i);
        
        tgtAtomCoords[i] = coords_func(atom);

        if (tgt_env_changed) {
            tgtAtomCharges[i] = ForceField::getMMFF94Charge(atom);

            getVdWParameters(atom, tgt_env, tgtAtomVdWParams[i]);
        }
    }
    
    tgtAtomOctree->initialize(tgtAtomCoords);

    tgtPharmGenerator.setAtom3DCoordinatesFunction(TargetAtomCoordsFunc(tgt_env, tgtAtomCoords));
    tgtPharmGenerator.generate(tgt_env, tgtPharmacophore);

    for (auto& ftr_ss : tgtFtrSubsets)
        ftr_ss.features.clear();

    for (auto& ftr : tgtPharmacophore) {
        unsigned int ext_type = perceiveExtendedType(ftr, false);
        
        if (ext_type > FeatureType::MAX_EXT_TYPE) // sanity check
            continue;

        if (ext_type == FeatureType::HYDROPHOBIC)
            setWeight(ftr, getHydrophobicity(ftr));
        
        tgtFtrSubsets[ext_type].features.push_back(&ftr);
    }

    for (auto& ftr_ss : tgtFtrSubsets) {
        std::size_t num_ftrs = ftr_ss.features.size();
        
        ftr_ss.ftrCoords.resize(num_ftrs);

        for (std::size_t i = 0; i < num_ftrs; i++) 
            ftr_ss.ftrCoords[i] = get3DCoordinates(*ftr_ss.features[i]);

        if (!ftr_ss.octree)
            ftr_ss.octree.reset(new Octree());

        ftr_ss.octree->initialize(ftr_ss.ftrCoords);
    }
}

void GRAIL::GRAILDescriptorCalculator::initLigandData(const Chem::MolecularGraph& ligand)
{
    using namespace Pharm;
    using namespace Chem;

    numLigAtoms = ligand.getNumAtoms();
        
    ligHeavyAtoms.clear();

    if (ligAtomCharges.size() < numLigAtoms)
        ligAtomCharges.resize(numLigAtoms);

    if (ligAtomVdWParams.size() < numLigAtoms)
        ligAtomVdWParams.resize(numLigAtoms);

    ligDescriptor[TOTAL_HYD] = 0.0;
    ligDescriptor[LOGP] = 0.0;
    ligDescriptor[TPSA] = ligTPSACalculator.calculate(ligand);
    ligDescriptor[HVY_ATOM_COUNT] = MolProp::getHeavyAtomCount(ligand);
    ligDescriptor[ROT_BOND_COUNT] = MolProp::getRotatableBondCount(ligand);
        
    for (std::size_t i = 0; i < numLigAtoms; i++) {
        const Atom& atom = ligand.getAtom(i);

        if (getType(atom) != AtomType::H)
            ligHeavyAtoms.push_back(i);

        ligAtomCharges[i] = ForceField::getMMFF94Charge(atom);

        getVdWParameters(atom, ligand, ligAtomVdWParams[i]);

        ligDescriptor[LOGP] += MolProp::getHydrophobicity(atom); 
    }
    
    ligPharmGenerator.generate(ligand, ligPharmacophore);
    
    for (auto& il : ligFtrSubsets)
        il.clear();

    std::size_t num_ftrs = ligPharmacophore.getNumFeatures();

    if (ligFtrWeights.size() < num_ftrs)
        ligFtrWeights.resize(num_ftrs);

    if (ligFtrAtoms.size() < num_ftrs)
        ligFtrAtoms.resize(num_ftrs);

    ligFtrCoords.resize(num_ftrs);
    
    for (std::size_t i = 0; i < num_ftrs; i++) {
        const Feature& ftr = ligPharmacophore.getFeature(i);
        const Fragment::SharedPointer& ftr_substruct = getSubstructure(ftr);

        ligFtrAtoms[i].clear();

        for (const auto& atom : ftr_substruct->getAtoms())
            if (getType(atom) != AtomType::H)
                ligFtrAtoms[i].push_back(ligand.getAtomIndex(atom));
        
        unsigned int ext_type = perceiveExtendedType(ftr, true);

        if (ext_type == FeatureType::HYDROPHOBIC) {
            ligFtrWeights[i] = getHydrophobicity(ftr);
            ligDescriptor[TOTAL_HYD] += ligFtrWeights[i];
            
        } else
            ligFtrWeights[i] = 1.0;

        if (ext_type > FeatureType::MAX_EXT_TYPE) // sanity check
            continue;

        ligFtrSubsets[ext_type].push_back(i);
    }

    for (std::size_t i = 0; i < sizeof(LIGAND_DESCR_FTR_TYPES) / sizeof(LigandFtrType); i++) {
        const LigandFtrType& ftr_type = LIGAND_DESCR_FTR_TYPES[i];
        const IndexList& ftrs = ligFtrSubsets[ftr_type.type];
        
        if (!ftr_type.isHBD) {
            ligDescriptor[i] = ftrs.size();
            continue;
        }

        // for H-donor atoms the number of attached Hs has to be considered 
        ligDescriptor[i] = 0;

        for (auto ftr_idx : ftrs) {
            const Feature& ftr = ligPharmacophore.getFeature(ftr_idx);
            const Fragment::SharedPointer& ftr_substruct = getSubstructure(ftr);

            for (const auto& atom : ftr_substruct->getAtoms()) {
                if (getType(atom) == AtomType::H)
                    continue;

                ligDescriptor[i] += MolProp::getAtomCount(atom, ligand, AtomType::H);
                break;
            }
        }
    }
}

void GRAIL::GRAILDescriptorCalculator::calculate(const Math::Vector3DArray& atom_coords, Math::DVector& descr, bool update_lig_part)
{
    if (atom_coords.getSize() != numLigAtoms)
        throw Base::SizeError("GRAILDescriptorCalculator: atom coordinates array size does not match number of atoms");
    
    if (descr.getSize() < TOTAL_DESCRIPTOR_SIZE)
        descr.resize(TOTAL_DESCRIPTOR_SIZE);

    std::size_t idx = (update_lig_part ? std::size_t(0) : LIGAND_DESCRIPTOR_SIZE);

    if (update_lig_part)
        for ( ; idx < LIGAND_DESCRIPTOR_SIZE; idx++)
            descr[idx] = ligDescriptor[idx];

    calcLigFtrCoordinates(atom_coords.getData());
    calcTgtEnvHBAHBDOccupations(atom_coords.getData(), descr, idx);
    calcFeatureInteractionScores(descr, idx);
    calcElectrostaticInteractionEnergy(atom_coords.getData(), descr, idx);
    calcVdWInteractionEnergy(atom_coords.getData(), descr, idx);
}

void GRAIL::GRAILDescriptorCalculator::calcLigFtrCoordinates(const Math::Vector3DArray::StorageType& atom_coords)
{
    for (std::size_t i = 0, num_ftrs = ligFtrCoords.size(); i < num_ftrs; i++) {
        Math::Vector3D& ftr_pos = ligFtrCoords[i];
        const IndexList& ftr_atoms  = ligFtrAtoms[i];
        std::size_t num_atoms = ftr_atoms.size();
        
        if (num_atoms == 0) // should never happen!
            continue;
        
        if (num_atoms == 1) {
            ftr_pos = atom_coords[ftr_atoms[0]];
            continue;
        }

        ftr_pos.clear();
        
        for (auto atom_idx : ftr_atoms)
            ftr_pos.plusAssign(atom_coords[atom_idx]);

        ftr_pos /= num_atoms;
    }
}

void GRAIL::GRAILDescriptorCalculator::calcTgtEnvHBAHBDOccupations(const Math::Vector3DArray::StorageType& atom_coords,
                                                                   Math::DVector& descr, std::size_t& idx)
{
    calcTgtEnvHBAHBDOccupation(atom_coords, descr, FeatureType::H_BOND_ACCEPTOR_N, true, idx);
    calcTgtEnvHBAHBDOccupation(atom_coords, descr, FeatureType::H_BOND_ACCEPTOR_O, true, idx);
    calcTgtEnvHBAHBDOccupation(atom_coords, descr, FeatureType::H_BOND_ACCEPTOR_S, true, idx);

    calcTgtEnvHBAHBDOccupation(atom_coords, descr, FeatureType::H_BOND_DONOR_N, false, idx);
    calcTgtEnvHBAHBDOccupation(atom_coords, descr, FeatureType::H_BOND_DONOR_O, false, idx);
    calcTgtEnvHBAHBDOccupation(atom_coords, descr, FeatureType::H_BOND_DONOR_S, false, idx);
}

void GRAIL::GRAILDescriptorCalculator::calcTgtEnvHBAHBDOccupation(const Math::Vector3DArray::StorageType& atom_coords,
                                                                  Math::DVector& descr, unsigned int tgt_ftr_type,
                                                                  bool is_hba_type, std::size_t& idx)
{
    Pharm::HBondingInteractionScore scoring_func(is_hba_type);
    const FeatureSubset& tgt_ftr_ss = tgtFtrSubsets[tgt_ftr_type];
    double score_sum = 0.0;
    double score_max = 0.0;

    for (auto lig_atom_idx : ligHeavyAtoms) {
        const Math::Vector3D& lig_atom_pos = atom_coords[lig_atom_idx];
        double max_score = 0.0;

        tmpIndexList.clear();
        tgt_ftr_ss.octree->radiusNeighbors<Octree::L2Distance>(lig_atom_pos, FEATURE_DISTANCE_CUTOFF, std::back_inserter(tmpIndexList));

        for (auto tgt_ftr_idx : tmpIndexList) {
            double s = scoring_func(lig_atom_pos, *tgt_ftr_ss.features[tgt_ftr_idx]);

            max_score = std::max(max_score, s);
            score_sum += s;
        }

        score_max += max_score;
    }

    descr[idx++] = score_sum;
    descr[idx++] = score_max;
}

void GRAIL::GRAILDescriptorCalculator::calcFeatureInteractionScores(Math::DVector& descr, std::size_t& idx)
{
    std::call_once(initFtrInteractionFuncListFlag, &initFtrInteractionFuncList);

    for (const auto& func_data : ftrInteractionFuncList) {
        const IndexList& lig_ftrs = ligFtrSubsets[func_data.ligFtrType];
        const FeatureSubset& tgt_ftr_ss = tgtFtrSubsets[func_data.tgtFtrType];
        double score_sum = 0.0;
        double score_max = 0.0;
        
        for (auto lig_ftr_idx : lig_ftrs) {
            double lig_ftr_wt = ligFtrWeights[lig_ftr_idx];
            const Math::Vector3D& lig_ftr_pos = ligFtrCoords[lig_ftr_idx];
            double max_score = 0.0;
            
            tmpIndexList.clear();
            tgt_ftr_ss.octree->radiusNeighbors<Octree::L2Distance>(lig_ftr_pos, FEATURE_DISTANCE_CUTOFF, std::back_inserter(tmpIndexList));
            
            for (auto tgt_ftr_idx : tmpIndexList) {
                double s = lig_ftr_wt * (*func_data.scoringFunc)(lig_ftr_pos, *tgt_ftr_ss.features[tgt_ftr_idx]);

                max_score = std::max(max_score, s);
                score_sum += s;
            }

            score_max += max_score;
        }

        descr[idx++] = score_sum;
        descr[idx++] = score_max;
    }
}

void GRAIL::GRAILDescriptorCalculator::calcElectrostaticInteractionEnergy(const Math::Vector3DArray::StorageType& atom_coords,
                                                                          Math::DVector& descr, std::size_t& idx)
{
    double energy = 0.0;
    double energy_sqrd_dist = 0.0;
    
    for (std::size_t i = 0; i < numLigAtoms; i++) {
        double la_charge = ligAtomCharges[i];
        const Math::Vector3D& la_pos = atom_coords[i];

        tmpIndexList.clear();
        tgtAtomOctree->radiusNeighbors<Octree::L2Distance>(la_pos, ESTAT_DISTANCE_CUTOFF, std::back_inserter(tmpIndexList));

        for (auto tgt_atom_idx : tmpIndexList) {
            double r_ij = ForceField::calcDistance<double>(la_pos, tgtAtomCoords[tgt_atom_idx]);
            double e = la_charge * tgtAtomCharges[tgt_atom_idx] / (r_ij * DIELECTRIC_CONST);

            energy += e;
            energy_sqrd_dist += e / r_ij;
        }
    }

    descr[idx++] = energy;
    descr[idx++] = energy_sqrd_dist;
}

/*
 * Uses a Morse potential:
 * V = D,i,j * (e^(-2 * alpha * (r,i,j - x,i,j)) - 2 * e^(-alpha * (r,i,j - x,i,j)))
 * D,i,j = sqrt(D,i * D,j)
 * x,i,j = sqrt(x,i * x,j) * 2^(1/6)
 */
void GRAIL::GRAILDescriptorCalculator::calcVdWInteractionEnergy(const Math::Vector3DArray::StorageType& atom_coords,
                                                                Math::DVector& descr, std::size_t idx)
{
    const double RMIN_FACT = std::pow(2, 1.0 / 6);
    const double ALPHA = 1.1;

    double energy_att = 0.0;
    double energy_rep = 0.0;
    
    for (std::size_t i = 0; i < numLigAtoms; i++) {
        const DoublePair& la_params = ligAtomVdWParams[i];
        const Math::Vector3D& la_pos = atom_coords[i];

        tmpIndexList.clear();
        tgtAtomOctree->radiusNeighbors<Octree::L2Distance>(la_pos, VDW_DISTANCE_CUTOFF, std::back_inserter(tmpIndexList));

        for (auto tgt_atom_idx : tmpIndexList) {
            const DoublePair& ta_params = tgtAtomVdWParams[tgt_atom_idx];

            double r_ij = ForceField::calcDistance<double>(la_pos, tgtAtomCoords[tgt_atom_idx]);
            double D_ij = std::sqrt(la_params.second * ta_params.second);
            double x_ij = RMIN_FACT * std::sqrt(la_params.first * ta_params.first);
            double r_delta = r_ij - x_ij;

            energy_att += -D_ij * 2 * std::exp(-ALPHA * r_delta);
            energy_rep += D_ij * std::exp(-2 * ALPHA * r_delta);
        }
    }

    descr[idx++] = energy_att;
    descr[idx++] = energy_rep;
}

void GRAIL::GRAILDescriptorCalculator::getVdWParameters(const Chem::Atom& atom, const Chem::MolecularGraph& molgraph, DoublePair& params) const
{
    using namespace ForceField;
    
    const UFFAtomTypePropertyTable::Entry& uff_props = UFFAtomTypePropertyTable::get()->getEntry(perceiveUFFType(atom, molgraph));

    if (!uff_props) {
        params.first = 0.0;
        params.second = 0.0;
        return;
    }
    
    params.first = uff_props.getVdWDistance();
    params.second = uff_props.getVdWEnergy();

    if (isPolarHydrogen(atom, molgraph))
        params.first *= VDW_POLAR_H_DIST_SCALING_FACTOR;
}
            
bool GRAIL::GRAILDescriptorCalculator::isPolarHydrogen(const Chem::Atom& atom, const Chem::MolecularGraph& molgraph) const
{
    using namespace Chem;

    if (getType(atom) != AtomType::H)
        return false;
    
    if (atom.getNumAtoms() != 1 || !molgraph.containsAtom(atom.getAtom(0)))
        return false;
        
    switch (getType(atom.getAtom(0))) {

        case AtomType::N:
        case AtomType::O:
        case AtomType::S:
            return true;
    }

    return false;
}

void GRAIL::GRAILDescriptorCalculator::initPharmGenerators()
{
    Pharm::HydrophobicAtomFeatureGenerator::SharedPointer tgt_h_gen(new Pharm::HydrophobicAtomFeatureGenerator());
    
    tgt_h_gen->setHydrophobicityThreshold(HYDROPHOBICIY_THRESHOLD);

    tgtPharmGenerator.setFeatureGenerator(FeatureType::HYDROPHOBIC, tgt_h_gen);
    tgtPharmGenerator.enableFeature(FeatureType::HALOGEN_BOND_ACCEPTOR, true);
    tgtPharmGenerator.enableFeature(FeatureType::NEGATIVE_IONIZABLE, false);

    Pharm::HydrophobicAtomFeatureGenerator::SharedPointer lig_h_gen(new Pharm::HydrophobicAtomFeatureGenerator());
    
    lig_h_gen->setHydrophobicityThreshold(HYDROPHOBICIY_THRESHOLD);

    ligPharmGenerator.setFeatureGenerator(FeatureType::HYDROPHOBIC, lig_h_gen);
}

void GRAIL::GRAILDescriptorCalculator::copyTgtFtrSubsets(const FeatureSubsetList& ftr_ss_list)
{
    for (std::size_t i = 0; i < (FeatureType::MAX_EXT_TYPE + 1); i++) {
        tgtFtrSubsets[i].features.clear();

        for (std::size_t j = 0, num_ftrs = ftr_ss_list[i].features.size(); j < num_ftrs; j++)
            tgtFtrSubsets[i].features.push_back(&tgtPharmacophore.getFeature(ftr_ss_list[i].features[j]->getIndex()));

        tgtFtrSubsets[i].ftrCoords = ftr_ss_list[i].ftrCoords;
    
        if (!tgtFtrSubsets[i].octree)
            tgtFtrSubsets[i].octree.reset(new Octree());
        
        tgtFtrSubsets[i].octree->initialize(tgtFtrSubsets[i].ftrCoords);
    }
}

inline const Math::Vector3D& GRAIL::GRAILDescriptorCalculator::TargetAtomCoordsFunc::operator()(const Chem::Atom& atom) const
{
    return (*coords)[tgtEnv->getAtomIndex(atom)];
}
