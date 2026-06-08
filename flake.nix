{
  description = "Monitoramento de emissões de carbono corporativas";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = ["x86_64-linux"];

      perSystem = {
        config,
        pkgs,
        lib,
        system,
        ...
      }: let
        py = pkgs.python313Packages;
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            py.python

            pkgs.uv
            pkgs.ty
            pkgs.ruff
          ];

          shellHook = ''
            REPO_ROOT=$(git rev-parse --show-toplevel)

            cd "$REPO_ROOT"
            
            uv sync
            . .venv/bin/activate
          '';

          PYTHONPATH = "src:src/svd";
          LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib";
        };
      };
    };
}
