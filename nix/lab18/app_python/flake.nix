{
  description = "DevOps Info Service - flake for reproducible builds";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11"; # example pin, update via `nix flake update`
  };

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      app = import ./default.nix { inherit pkgs; };
    in
    {
      packages.${system} = {
        default = app;
        dockerImage = import ./docker.nix { inherit pkgs; };
      };

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [ python313 python313Packages.fastapi python313Packages.uvicorn ];
      };
    };
}
