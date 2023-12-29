{
  description = "ralismark.xyz";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "heron";
          version = "0.1.0";
          src = ./.;
          site = ./site;

          buildInputs = [
            pkgs.graphviz
            pkgs.nodePackages.katex
            (pkgs.python3.withPackages (p: with p; [
              jinja2
              pyyaml
              mistune
              watchdog
              frozendict
              pygments
              libsass
              graphviz
            ]))
          ];

          buildPhase = ''
            PYTHONPATH=.
            python -m heron build -o $out $site/main.py
          '';

          shellHook = ''
            PYTHONPATH=.
          '';
        };
      });
}