/* 
 * TautomerGenerator.cpp 
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

#include <algorithm>
#include <iterator>
#include <functional>

#include "CDPL/Chem/TautomerGenerator.hpp"
#include "CDPL/Chem/BasicMolecule.hpp"
#include "CDPL/Chem/AtomFunctions.hpp"
#include "CDPL/Chem/BondFunctions.hpp"
#include "CDPL/Chem/Entity3DFunctions.hpp"
#include "CDPL/Chem/MoleculeFunctions.hpp"
#include "CDPL/Chem/MolecularGraphFunctions.hpp"
#include "CDPL/Chem/AtomType.hpp"
#include "CDPL/Chem/HybridizationState.hpp"
#include "CDPL/Chem/AtomConfiguration.hpp"
#include "CDPL/Chem/BondConfiguration.hpp"
#include "CDPL/Chem/StereoDescriptor.hpp"
#include "CDPL/Internal/AtomFunctions.hpp"
#include "CDPL/Internal/BondFunctions.hpp"
#include "CDPL/Internal/SHA1.hpp"


namespace
{

    const std::size_t MAX_MOLECULE_CACHE_SIZE = 5000;
}


using namespace CDPL;


Chem::TautomerGenerator::TautomerGenerator():
    molCache(MAX_MOLECULE_CACHE_SIZE),
    mode(TOPOLOGICALLY_UNIQUE), regStereo(true), regIsotopes(true)
{
    molCache.setCleanupFunction(&BasicMolecule::clear);
}

Chem::TautomerGenerator::TautomerGenerator(const TautomerGenerator& gen):
    molCache(MAX_MOLECULE_CACHE_SIZE),
    callbackFunc(gen.callbackFunc), mode(gen.mode), regStereo(gen.regStereo), regIsotopes(gen.regIsotopes)
{
    molCache.setCleanupFunction(&BasicMolecule::clear);

    std::transform(gen.tautRules.begin(), gen.tautRules.end(), std::back_inserter(tautRules), std::bind(&TautomerizationRule::clone, std::placeholders::_1));
}

Chem::TautomerGenerator& Chem::TautomerGenerator::operator=(const TautomerGenerator& gen) 
{
    if (this == &gen)
        return *this;

    callbackFunc = gen.callbackFunc;
    mode = gen.mode;
    regStereo = gen.regStereo;
    regIsotopes = gen.regIsotopes;

    tautRules.clear();

    std::transform(gen.tautRules.begin(), gen.tautRules.end(), std::back_inserter(tautRules), 
                   std::bind(&TautomerizationRule::clone, std::placeholders::_1));

    return *this;
}

void Chem::TautomerGenerator::addTautomerizationRule(const TautomerizationRule::SharedPointer& rule)
{
    tautRules.push_back(rule);
}

const Chem::TautomerizationRule::SharedPointer& Chem::TautomerGenerator::getTautomerizationRule(std::size_t idx) const
{
    if (idx >= tautRules.size())
        throw Base::IndexError("TautomerGenerator: rule index out of bounds");

    return tautRules[idx];
}

void Chem::TautomerGenerator::removeTautomerizationRule(std::size_t idx)
{
    if (idx >= tautRules.size())
        throw Base::IndexError("TautomerGenerator: rule index out of bounds");

    tautRules.erase(tautRules.begin() + idx);
}

std::size_t Chem::TautomerGenerator::getNumTautomerizationRules() const
{
    return tautRules.size();
}

void Chem::TautomerGenerator::setCallbackFunction(const CallbackFunction& func)
{
    callbackFunc = func;
}

const Chem::TautomerGenerator::CallbackFunction& Chem::TautomerGenerator::getCallbackFunction() const
{
    return callbackFunc;
}

void Chem::TautomerGenerator::setMode(Mode mode)
{
    this->mode = mode;
}

Chem::TautomerGenerator::Mode Chem::TautomerGenerator::getMode() const
{
    return mode;
}

void Chem::TautomerGenerator::regardStereochemistry(bool regard)
{
    regStereo = regard;
}

bool Chem::TautomerGenerator::stereochemistryRegarded() const
{
    return regStereo;
}

void Chem::TautomerGenerator::regardIsotopes(bool regard)
{
    regIsotopes = regard;
}

bool Chem::TautomerGenerator::isotopesRegarded() const
{
    return regIsotopes;
}

void Chem::TautomerGenerator::setCustomSetupFunction(const CustomSetupFunction& func)
{
    customSetupFunc = func;
}

void Chem::TautomerGenerator::generate(const MolecularGraph& molgraph)
{
    if (!callbackFunc)
        return;

    if (!init(molgraph))
        return;

    TautRuleList::const_iterator rules_beg = tautRules.begin();
    TautRuleList::const_iterator rules_end = tautRules.end();

    while (!nextGeneration.empty()) {
        currGeneration.swap(nextGeneration);

        while (!currGeneration.empty()) {
            MoleculePtr mol = currGeneration.back();
            currGeneration.pop_back();

            for (TautRuleList::const_iterator r_it = rules_beg; r_it != rules_end; ++r_it) {
                TautomerizationRule& rule = **r_it;

                if (!rule.setup(*mol))
                    continue;

                while (true) {
                    MoleculePtr tautomer = molCache.get();

                    if (rule.generate(*tautomer)) {
                        if (!addNewTautomer(tautomer)) 
                            continue;

                        if (!callbackFunc(*tautomer))
                            return;

                    } else
                        break;
                }
            }
        }
    }
}

bool Chem::TautomerGenerator::init(const MolecularGraph& molgraph)
{
    tautHashCodes.clear();
    currGeneration.clear();
    nextGeneration.clear();

    extractStereoCenters(molgraph);
    initHashCalculator();

    MoleculePtr mol = copyInputMolGraph(molgraph);

    addNewTautomer(mol);

    return callbackFunc(*mol);
}

void Chem::TautomerGenerator::initHashCalculator()
{
    unsigned int atom_flags = AtomPropertyFlag::TYPE | AtomPropertyFlag::FORMAL_CHARGE;
    unsigned int bond_flags = BondPropertyFlag::ORDER;

    if (regIsotopes) 
        atom_flags |= AtomPropertyFlag::ISOTOPE;

    if (regStereo) {
        atom_flags |= AtomPropertyFlag::CIP_CONFIGURATION;
        bond_flags |= BondPropertyFlag::CIP_CONFIGURATION;
    }

    hashCalculator.setAtomHashSeedFunction(HashCodeCalculator::DefAtomHashSeedFunctor(hashCalculator, atom_flags));
    hashCalculator.setBondHashSeedFunction(HashCodeCalculator::DefBondHashSeedFunctor(bond_flags));
    hashCalculator.includeGlobalStereoFeatures(regStereo);
}

Chem::TautomerGenerator::MoleculePtr Chem::TautomerGenerator::copyInputMolGraph(const MolecularGraph& molgraph)
{
    MoleculePtr mol_copy = molCache.get();

    for (MolecularGraph::ConstAtomIterator it = molgraph.getAtomsBegin(), end = molgraph.getAtomsEnd(); it != end; ++it) {
        const Atom& atom = *it;
        Atom& atom_copy = mol_copy->addAtom();

        setType(atom_copy, getType(atom));
        setFormalCharge(atom_copy, getFormalCharge(atom));
        setUnpairedElectronCount(atom_copy, getUnpairedElectronCount(atom));

        if (regIsotopes)
            setIsotope(atom_copy, getIsotope(atom));

        if (has3DCoordinates(atom))
            set3DCoordinates(atom_copy, get3DCoordinates(atom));

        if (has2DCoordinates(atom))
            set2DCoordinates(atom_copy, get2DCoordinates(atom));
    }

    for (MolecularGraph::ConstBondIterator it = molgraph.getBondsBegin(), end = molgraph.getBondsEnd(); it != end; ++it) {
        const Bond& bond = *it;
        Bond& bond_copy = mol_copy->addBond(molgraph.getAtomIndex(bond.getBegin()), molgraph.getAtomIndex(bond.getEnd()));

        setOrder(bond_copy, getOrder(bond));
        set2DStereoFlag(bond_copy, get2DStereoFlag(bond));
    }

    calcImplicitHydrogenCounts(*mol_copy, true);
    makeHydrogenComplete(*mol_copy);

    std::for_each(mol_copy->getAtomsBegin(), mol_copy->getAtomsEnd(), std::bind(&setImplicitHydrogenCount, std::placeholders::_1, 0));

    return mol_copy;
}

void Chem::TautomerGenerator::extractStereoCenters(const MolecularGraph& molgraph)
{
    if (!regStereo)
        return;

    extractAtomStereoCenters(molgraph);
    extractBondStereoCenters(molgraph);
}

void Chem::TautomerGenerator::extractAtomStereoCenters(const MolecularGraph& molgraph)
{
    atomStereoCenters.clear();

    std::size_t atom_idx = 0;

    for (MolecularGraph::ConstAtomIterator it = molgraph.getAtomsBegin(), end = molgraph.getAtomsEnd(); it != end; ++it, atom_idx++) {
        const Atom& atom = *it;
    
        if (!hasStereoDescriptor(atom))
            continue;

        const StereoDescriptor& descr = getStereoDescriptor(atom);
        unsigned int config = descr.getConfiguration();

        if (config != AtomConfiguration::R && config != AtomConfiguration::S)
            continue;

        std::size_t num_ref_atoms = descr.getNumReferenceAtoms();

        if (num_ref_atoms < 3)
            continue;

        const Atom* const* sto_ref_atoms = descr.getReferenceAtoms();

        StereoCenter sto_ctr;
        const Atom* new_ref_atoms[4];
        std::size_t i = 0;

        for (std::size_t j = 0; j < num_ref_atoms; j++) {
            const Atom* ref_atom = sto_ref_atoms[j];
        
            if (getType(*ref_atom) == AtomType::H)
                continue;

            if (!molgraph.containsAtom(*ref_atom))
                continue;

            const Bond* ref_bond = atom.findBondToAtom(*ref_atom);

            if (!ref_bond)
                continue;

            if (!molgraph.containsBond(*ref_bond))
                continue;

            new_ref_atoms[i] = ref_atom;
            sto_ctr[i + 2] = molgraph.getAtomIndex(*ref_atom);
            i++;
        }

        if (i < 3)
            continue;

        if (i != num_ref_atoms) {
            unsigned int perm_parity = (i == 3 ? descr.getPermutationParity(*new_ref_atoms[0], *new_ref_atoms[1], *new_ref_atoms[2]) :
                                        descr.getPermutationParity(*new_ref_atoms[0], *new_ref_atoms[1], *new_ref_atoms[2], *new_ref_atoms[3]));

            if (perm_parity != 1 && perm_parity != 2)
                continue;

            switch (config) {

                case AtomConfiguration::S:
                    config = (perm_parity == 2 ? AtomConfiguration::S : AtomConfiguration::R);
                    break;

                case AtomConfiguration::R:
                    config = (perm_parity == 2 ? AtomConfiguration::R : AtomConfiguration::S);
                    break;

                default:
                    continue;
            }
        }

        sto_ctr[0] = atom_idx;
        sto_ctr[1] = config;

        if (i == 3)
            sto_ctr[5] = sto_ctr[4];

        atomStereoCenters.push_back(sto_ctr);
    }
}

void Chem::TautomerGenerator::extractBondStereoCenters(const MolecularGraph& molgraph)
{
    bondStereoCenters.clear();

    for (MolecularGraph::ConstBondIterator it = molgraph.getBondsBegin(), end = molgraph.getBondsEnd(); it != end; ++it) {
        const Bond& bond = *it;
    
        if (!hasStereoDescriptor(bond))
            continue;

        const StereoDescriptor& descr = getStereoDescriptor(bond);
        unsigned int config = descr.getConfiguration();

        if (config != BondConfiguration::CIS && config != BondConfiguration::TRANS)
            continue;

        if (!descr.isValid(bond))
            continue;

        const Atom* const* sto_ref_atoms = descr.getReferenceAtoms();

        StereoCenter sto_ctr;
        const Atom* new_ref_atoms[2] = { 0, 0 };

        for (std::size_t i = 0; i < 2; i++) {
            Atom::ConstAtomIterator atoms_end = sto_ref_atoms[i + 1]->getAtomsEnd();
            Atom::ConstBondIterator b_it = sto_ref_atoms[i + 1]->getBondsBegin();

            for (Atom::ConstAtomIterator a_it = sto_ref_atoms[i + 1]->getAtomsBegin(); a_it != atoms_end; ++a_it, ++b_it) {
                const Bond& nbr_bond = *b_it;

                if (&nbr_bond == &bond)
                    continue;

                if (!molgraph.containsBond(nbr_bond))
                    continue;

                const Atom& nbr_atom = *a_it;

                if (!molgraph.containsAtom(nbr_atom))
                    continue;

                if (getType(nbr_atom) == AtomType::H)
                    continue;

                new_ref_atoms[i] = &nbr_atom;
                sto_ctr[i == 0 ? 1 : 4] = molgraph.getAtomIndex(nbr_atom);
                break;
            }
        }

        if (!new_ref_atoms[0] || !new_ref_atoms[1])
            continue;

        sto_ctr[2] = molgraph.getAtomIndex(*sto_ref_atoms[1]);
        sto_ctr[3] = molgraph.getAtomIndex(*sto_ref_atoms[2]);

        switch (config) {

            case BondConfiguration::CIS:
                config = ((new_ref_atoms[0] == sto_ref_atoms[0]) ^ (new_ref_atoms[1] == sto_ref_atoms[3]) ?
                          BondConfiguration::TRANS : BondConfiguration::CIS);
                break;

            case BondConfiguration::TRANS:
                config = ((new_ref_atoms[0] == sto_ref_atoms[0]) ^ (new_ref_atoms[1] == sto_ref_atoms[3]) ? 
                          BondConfiguration::CIS : BondConfiguration::TRANS);
                break;

            default:
                continue;
        }

        sto_ctr[0] = config;

        bondStereoCenters.push_back(sto_ctr);
    }
}

bool Chem::TautomerGenerator::addNewTautomer(const MoleculePtr& mol)
{
    if (regStereo) {
        perceiveHybridizationStates(*mol, true);

        for (StereoCenterList::const_iterator it = atomStereoCenters.begin(), end = atomStereoCenters.end(); it != end; ++it) {
            const StereoCenter& sto_ctr = *it;

            Atom& atom = mol->getAtom(sto_ctr[0]);

            if (getHybridizationState(atom) != HybridizationState::SP3)
                continue;

            StereoDescriptor descr = (sto_ctr[4] == sto_ctr[5] ? StereoDescriptor(sto_ctr[1], mol->getAtom(sto_ctr[2]), mol->getAtom(sto_ctr[3]), mol->getAtom(sto_ctr[4])) :
                                      StereoDescriptor(sto_ctr[1], mol->getAtom(sto_ctr[2]), mol->getAtom(sto_ctr[3]), mol->getAtom(sto_ctr[4]), mol->getAtom(sto_ctr[5])));

            if (descr.isValid(atom))
                setStereoDescriptor(atom, descr);
        }

        for (StereoCenterList::const_iterator it = bondStereoCenters.begin(), end = bondStereoCenters.end(); it != end; ++it) {
            const StereoCenter& sto_ctr = *it;
            Atom& atom1 = mol->getAtom(sto_ctr[2]);
            Atom& atom2 = mol->getAtom(sto_ctr[3]);
            Bond* bond = atom1.findBondToAtom(atom2);

            if (!bond)
                continue;

            if (getOrder(*bond) != 2)
                continue;

            StereoDescriptor descr = StereoDescriptor(sto_ctr[0], mol->getAtom(sto_ctr[1]), atom1, atom2, mol->getAtom(sto_ctr[4]));

            if (descr.isValid(*bond)) 
                setStereoDescriptor(*bond, descr);
        }

        if (mode == TOPOLOGICALLY_UNIQUE) {
            perceiveSSSR(*mol, true);
            setAromaticityFlags(*mol, true);
            calcCIPPriorities(*mol, true);
            calcAtomCIPConfigurations(*mol, true);
            calcBondCIPConfigurations(*mol, true);
        }
    }

    std::uint64_t hash = calcTautomerHashCode(*mol);

    if (tautHashCodes.insert(hash).second) {
        if (customSetupFunc)
            customSetupFunc(*mol);

        nextGeneration.push_back(mol);
        return true;
    }

    return false;
}

std::uint64_t Chem::TautomerGenerator::calcTautomerHashCode(const BasicMolecule& tautomer)
{
    if (mode == TOPOLOGICALLY_UNIQUE)
        return hashCalculator.calculate(tautomer);

    BondDescriptor bond_desc;

    tautomerBonds.clear();

    for (BasicMolecule::ConstBondIterator it = tautomer.getBondsBegin(), end = tautomer.getBondsEnd(); it != end; ++it) {
        const Bond& bond = *it;

        if (mode == GEOMETRICALLY_UNIQUE) {
            if (regIsotopes) {
                if (Internal::isOrdinaryHydrogen(bond.getBegin(), tautomer) || Internal::isOrdinaryHydrogen(bond.getEnd(), tautomer)) 
                    continue;
            } else if (Internal::isHydrogenBond(bond)) 
                continue;
        }

        std::size_t atom1_idx = bond.getBegin().getIndex();
        std::size_t atom2_idx = bond.getEnd().getIndex();

        if (atom2_idx > atom1_idx)
            std::swap(atom1_idx, atom2_idx);

        bond_desc[0] = atom1_idx;
        bond_desc[1] = atom2_idx;
        bond_desc[2] = getOrder(bond);

        tautomerBonds.push_back(bond_desc);
    }

    std::sort(tautomerBonds.begin(), tautomerBonds.end());

    shaInput.clear();

    for (BondDescrArray::const_iterator it = tautomerBonds.begin(), end = tautomerBonds.end(); it != end; ++it) {
        const BondDescriptor& descr = *it;

        shaInput.push_back(descr[0]);
        shaInput.push_back(descr[1]);
        shaInput.push_back(descr[2]);
    }

    Internal::SHA1 sha;
    std::uint8_t sha_hash[Internal::SHA1::HASH_SIZE];

    sha.input(shaInput.begin(), shaInput.end());
    sha.getResult(&sha_hash[0]);

    std::uint64_t hash_code = 0;

    for (std::size_t i = 0; i < Internal::SHA1::HASH_SIZE; i++) 
        hash_code = hash_code ^ (std::uint64_t(sha_hash[i]) << ((i % 8) * 8));

    return hash_code;
}
