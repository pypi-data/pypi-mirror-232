confgen
=======

The program :program:`confgen` has been published under the name **CONFORGE** and generates high-quality
conformer ensembles for a set of given input molecules.
Details regarding the implementation and performance of CONFORGE can be found in :cite:`doi:10.1021/acs.jcim.3c00563`.

Built-in torsion rules are based on the torsion library jointly developed by the
University of Hamburg, Center for Bioinformatics, Hamburg, Germany andF. Hoffmann-La-Roche Ltd., Basel, Switzerland
:cite:`doi:10.1021/jm3016816`:cite:`doi:10.1021/acs.jcim.5b00522`.

Synopsis
--------

  :program:`confgen` [-hVvptRHAuSszYMW] [-c arg] [-l arg] [-f arg] [-C arg] [-m arg] [-e arg] [-r arg] [-n arg] [-N arg] [-d arg] [-q arg] [-D arg] [-E arg] [-T arg] [-X arg] [-L arg] [-x arg] [-y arg] [-Z arg] [-P arg] [-w arg] [-k arg] [-K arg] [-B arg] [-b arg] [-g arg] [-G arg] [-I arg] [-O arg] [-F arg] -i arg [arg]... -o arg

Mandatory options
-----------------

  -i [ --input ] arg

    Specifies one or more input file(s) with molecules for which conformers have to 
    be generated.
    
    Supported Input Formats:
     - JME Molecular Editor String (.jme)
     - MDL Structure-Data File (.sdf, .sd)
     - MDL Molfile (.mol)
     - Daylight SMILES String (.smi)
     - IUPAC International Chemical Identifier (.inchi, .ichi)
     - Native CDPL-Format (.cdf)
     - Tripos Sybyl MOL2 File (.mol2)
     - GZip-Compressed MDL Structure-Data File (.sdf.gz, .sd.gz, .sdz)
     - BZip2-Compressed MDL Structure-Data File (.sdf.bz2, .sd.bz2)
     - GZip-Compressed Native CDPL-Format (.cdf.gz)
     - BZip2-Compressed Native CDPL-Format (.cdf.bz2)
     - GZip-Compressed Daylight SMILES String (.smi.gz)
     - BZip2-Compressed Daylight SMILES String (.smi.bz2)
     - GZip-Compressed Tripos Sybyl MOL2 File (.mol2.gz)
     - BZip2-Compressed Tripos Sybyl MOL2 File (.mol2.bz2)
     - CDPL Conformer Generator Fragment Library Format (.cfl, .cdf)

  -o [ --output ] arg

    Specifies the output file where the generated conformers will be stored.
    
    Supported Output Formats:
     - MDL Structure-Data File (.sdf, .sd)
     - MDL Molfile (.mol)
     - Native CDPL-Format (.cdf)
     - Tripos Sybyl MOL2 File (.mol2)
     - GZip-Compressed MDL Structure-Data File (.sdf.gz, .sd.gz, .sdz)
     - BZip2-Compressed MDL Structure-Data File (.sdf.bz2, .sd.bz2)
     - GZip-Compressed Native CDPL-Format (.cdf.gz)
     - BZip2-Compressed Native CDPL-Format (.cdf.bz2)
     - GZip-Compressed Tripos Sybyl MOL2 File (.mol2.gz)
     - BZip2-Compressed Tripos Sybyl MOL2 File (.mol2.bz2)

Other options
-------------
   
  -h [ --help ] [=arg(=SHORT)]

    Print help message and exit (ABOUT, USAGE, SHORT, ALL or 'name of option', default: 
    SHORT).

  -V [ --version ] 

    Print version information and exit.

  -v [ --verbosity ] [=arg(=VERBOSE)]

    Verbosity level of information output (QUIET, ERROR, INFO, VERBOSE, DEBUG, default: 
    INFO).

  -c [ --config ] arg

    Use file with program options.

  -l [ --log-file ] arg

    Redirect text-output to file.

  -p [ --progress ] [=arg(=1)]

    Show progress bar (default: true).

  -f [ --failed ] arg

    Specifies the output file for molecules where conformer generation failed.
    
    Supported Output Formats:
     - JME Molecular Editor String (.jme)
     - MDL Structure-Data File (.sdf, .sd)
     - MDL Molfile (.mol)
     - Daylight SMILES String (.smi)
     - Daylight SMARTS String (.sma)
     - IUPAC International Chemical Identifier (.inchi, .ichi)
     - Native CDPL-Format (.cdf)
     - Tripos Sybyl MOL2 File (.mol2)
     - GZip-Compressed MDL Structure-Data File (.sdf.gz, .sd.gz, .sdz)
     - BZip2-Compressed MDL Structure-Data File (.sdf.bz2, .sd.bz2)
     - GZip-Compressed Native CDPL-Format (.cdf.gz)
     - BZip2-Compressed Native CDPL-Format (.cdf.bz2)
     - GZip-Compressed Daylight SMILES String (.smi.gz)
     - BZip2-Compressed Daylight SMILES String (.smi.bz2)
     - GZip-Compressed Tripos Sybyl MOL2 File (.mol2.gz)
     - BZip2-Compressed Tripos Sybyl MOL2 File (.mol2.bz2)

  -t [ --num-threads ] [=arg(=4)]

    Number of parallel execution threads (default: no multithreading, implicit value: 
    4 threads, must be >= 0, 0 disables multithreading).

  -C [ --conf-gen-preset ] arg

    Conformer generation preset to use (SMALL_SET_DIVERSE, MEDIUM_SET_DIVERSE, LARGE_SET_DIVERSE, 
    SMALL_SET_DENSE, MEDIUM_SET_DENSE, LARGE_SET_DENSE, default: MEDIUM_SET_DIVERSE).

  -m [ --mode ] arg

    Conformer sampling mode (AUTO, STOCHASTIC, SYSTEMATIC, default: AUTO).

  -e [ --e-window ] arg

    Output energy window for generated conformers (default: 15.000000, must be >= 0).

  -r [ --rmsd ] arg

    Minimum RMSD for output conformer selection (default: 0.5000, must be >= 0, 0 disables 
    RMSD checking).

  -n [ --max-num-out-confs ] arg

    Maximum number of output conformers per molecule (default: 100, must be >= 0, 0 
    disables limit).

  -N [ --nitrogen-enum-mode ] arg

    Invertible nitrogen enumeration mode (NONE, ALL, UNSPECIFIED, default: UNSPECIFIED).

  -R [ --enum-rings ] [=arg(=1)]

    Enumerate ring conformers (only effective in systematic sampling mode, default: 
    true).

  -H [ --sample-het-hydrogens ] [=arg(=1)]

    Perform torsion sampling for hydrogens on hetero atoms (default: false).

  -A [ --tol-range-sampling ] [=arg(=1)]

    Additionally generate conformers for angles at the boundaries of the first torsion 
    angle tolerance range (only effective in systematic sampling mode, default: false).

  -u [ --include-input ] [=arg(=1)]

    Add input 3D-structure to output conformer ensemble (default: false).

  -S [ --from-scratch ] [=arg(=1)]

    Discard input 3D-coordinates and generate conformers from scratch (default: true).

  -d [ --systematic-search-force-field ] arg

    Search force field used in systematic sampling (MMFF94, MMFF94_NO_ESTAT, MMFF94S, 
    MMFF94S_XOOP, MMFF94S_RTOR, MMFF94S_RTOR_XOOP, MMFF94S_NO_ESTAT, MMFF94S_XOOP_NO_ESTAT, 
    MMFF94S_RTOR_NO_ESTAT, MMFF94S_RTOR_XOOP_NO_ESTAT, default: MMFF94S_RTOR_NO_ESTAT).

  -q [ --stochastic-search-force-field ] arg

    Search force field used in stochastic smapling (MMFF94, MMFF94_NO_ESTAT, MMFF94S, 
    MMFF94S_XOOP, MMFF94S_RTOR, MMFF94S_RTOR_XOOP, MMFF94S_NO_ESTAT, MMFF94S_XOOP_NO_ESTAT, 
    MMFF94S_RTOR_NO_ESTAT, MMFF94S_RTOR_XOOP_NO_ESTAT, default: MMFF94S_RTOR).

  -s [ --strict-param ] [=arg(=1)]

    Perform strict MMFF94 parameterization (default: true).

  -D [ --dielectric-const ] arg

    Dielectric constant used for the calculation of electrostatic interaction energies 
    (default: 80.0).

  -E [ --dist-exponent ] arg

    Distance exponent used for the calculation of electrostatic interaction energies 
    (default: 1.0).

  -T [ --timeout ] arg

    Time in seconds after which molecule conformer generation will be stopped (default: 
    3600 s, must be >= 0, 0 disables timeout).

  -X [ --max-num-rot-bonds ] arg

    Maximum number of allowed rotatable bonds, exceeding this limit causes molecule 
    conf. generation to fail (default: -1, negative values disable limit).

  -L [ --max-pool-size ] arg

    Puts an upper limit on the number of generated output conformer candidates (only 
    effective in systematic sampling mode, default: 10000, must be >= 0, 0 disables 
    limit).

  -x [ --max-num-sampled-confs ] arg

    Maximum number of sampled conformers (only effective in stochastic sampling mode, 
    default: 2000, must be >= 0, 0 disables limit).

  -y [ --conv-check-cycle-size ] arg

    Minimum number of duplicate conformers that have to be generated in succession to  
    consider convergence to be reached (only effective in stochastic sampling mode, 
    default: 100, must be > 0).

  -Z [ --mc-rot-bond-count-thresh ] arg

    Number of rotatable bonds in a ring above which stochastic sampling will be performed(only 
    effective in sampling mode AUTO, default: 10, must be > 0).

  -P [ --ref-tol ] arg

    Energy tolerance at which force field structure refinement stops (only effective 
    in stochastic sampling mode, default: 0.0010, must be >= 0, 0 results in refinement 
    until convergence).

  -w [ --max-ref-iter ] arg

    Maximum number of force field structure refinement iterations (only effective in 
    stochastic sampling mode, default: 0, must be >= 0, 0 disables limit).

  -k [ --add-tor-lib ] arg

    Torsion library to be used in addition to the built-in library (only effective in 
    systematic sampling mode).

  -K [ --set-tor-lib ] arg

    Torsion library used as a replacement for the built-in library (only effective in 
    systematic sampling mode).

  -B [ --frag-build-preset ] arg

    Fragment build preset to use (FAST, THOROUGH, only effective in systematic sampling 
    mode, default: FAST).

  -b [ --build-force-field ] arg

    Fragment build force field (MMFF94, MMFF94_NO_ESTAT, MMFF94S, MMFF94S_XOOP, MMFF94S_RTOR, 
    MMFF94S_RTOR_XOOP, MMFF94S_NO_ESTAT, MMFF94S_XOOP_NO_ESTAT, MMFF94S_RTOR_NO_ESTAT, 
    MMFF94S_RTOR_XOOP_NO_ESTAT, only effective in systematic sampling mode, default: 
    MMFF94S_RTOR_NO_ESTAT).

  -g [ --add-frag-lib ] arg

    Fragment library to be used in addition to the built-in library (only effective 
    in systematic sampling mode).

  -G [ --set-frag-lib ] arg

    Fragment library used as a replacement for the built-in library (only effective 
    in systematic sampling mode).

  -z [ --canonicalize ] [=arg(=1)]

    Canonicalize input molecules (default: false).

  -Y [ --energy-sd-entry ] [=arg(=1)]

    Output conformer energy in the structure data section of SD-files (default: false).

  -M [ --energy-comment ] [=arg(=1)]

    Output conformer energy in the comment field (if supported by output format, default: 
    false).

  -W [ --conf-idx-suffix ] [=arg(=1)]

    Append conformer index to the title of multiconf. output molecules (default: false).

  -I [ --input-format ] arg

    Allows to explicitly specify the format of the input file(s) by providing one of 
    the supported file-extensions (without leading dot!) as argument.
    This option is useful when the format cannot be auto-detected from the actual extension 
    of the file(s) (because missing, misleading or not supported).

  -O [ --output-format ] arg

    Allows to explicitly specify the output format by providing one of the supported 
    file-extensions (without leading dot!) as argument.
    This option is useful when the format cannot be auto-detected from the actual extension 
    of the file (because missing, misleading or not supported).
    Note that only storage formats make sense that allow to store atom 3D-coordinates!

  -F [ --failed-format ] arg

    Allows to explicitly specify the output format by providing one of the supported 
    file-extensions (without leading dot!) as argument.
    This option is useful when the format cannot be auto-detected from the actual extension 
    of the file (because missing, misleading or not supported).
