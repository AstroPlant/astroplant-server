with import <nixpkgs> {};
let
  python-packages = python-packages: [
    python-packages.pip
    python-packages.mysqlclient
  ];
  python-with-packages = python36.withPackages python-packages;
in  
  pkgs.mkShell {
    buildInputs = [
      bashInteractive
      ncurses
      python-with-packages
    ];
    shellHook = ''
      export PIP_PREFIX="$(pwd)/_build/pip_packages"
      export PYTHONPATH="$(pwd)/_build/pip_packages/lib/python3.6/site-packages:$PYTHONPATH" 
      unset SOURCE_DATE_EPOCH
    '';
  }

