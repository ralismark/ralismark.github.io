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
      rec {
        packages.heron = pkgs.writeShellApplication {
          name = "heron";
          runtimeInputs = [
            pkgs.graphviz
            pkgs.nodePackages.katex
            (pkgs.python3.withPackages (p: with p; [
              frozendict
              jinja2
              libsass
              mistune
              pygments
              pyyaml
              requests
              watchdog
            ]))
          ];

          text = ''
            export PYTHONPATH=''${HERONPATH-.}''${PYTHONPATH:+:}''${PYTHONPATH-}
            exec python -m heron "$@"
          '';
        };

        apps.default = {
          type = "app";
          program = pkgs.lib.getExe packages.heron;
        };

        lib.mkHeron = { name, src }: pkgs.runCommand name {
          buildInputs = [ packages.heron ];
        } ''
          HERONPATH=${./.} heron build ${src} -o $out
        '';

        packages.default = lib.mkHeron {
          name = "ralismark.xyz";
          src = "${./.}/site/main.py";
        };

      });
}
