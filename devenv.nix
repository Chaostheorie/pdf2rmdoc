{ inputs, pkgs, ... }:
{
  packages = [ inputs.nixos-ng.packages.${pkgs.system}.drawj2d ];

  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = builtins.readFile ./requirements.txt;
    };
  };
}
