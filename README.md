# Fira Code for Minecraft

This resource pack uses the original Fira Code 6.2 font for Minecraft's default text. [Caxton](https://modrinth.com/mod/caxton) renders the font, and [Respackopts](https://modrinth.com/mod/respackopts) adds a settings button to the Resource Packs screen.

## Install

1. Install Caxton, Respackopts, and Respackopts' required [LibJF](https://modrinth.com/mod/libjf) for your Minecraft version. For 26.2, use Fabric or NeoForge.
2. Download the ZIP for your version from [dist](dist). For 26.2, use [FiraCode-configurable-Caxton-MC26.2.zip](dist/26.2/FiraCode-configurable-Caxton-MC26.2.zip). Put the ZIP in your `resourcepacks` folder without extracting it.
3. Enable the pack in **Options > Resource Packs**. Click its settings button to choose the font weight and style.

The menu has separate weights for normal and bold text: Light, Regular, Retina, Medium, SemiBold, and Bold. You can also make normal text upright or oblique. Minecraft's italic formatting always uses the oblique face. The defaults are Regular upright for normal text and Bold for bold text.

## Versions and Modrinth uploads

There is one ZIP per stable Minecraft version with a published Caxton build, from 1.18.2 through 26.3. Upload the matching ZIP for each Minecraft version on Modrinth and list Caxton, Respackopts, and LibJF as required dependencies. The settings button needs a version of Respackopts for your mod loader.

To rebuild a single version or all versions, run:

```powershell
$env:UV_CACHE_DIR = "$PWD/.uv-cache"
uv run --python 3.12 --no-project --with fonttools==4.66.1 python build.py --version 26.2
uv run --python 3.12 --no-project --with fonttools==4.66.1 python build.py --all
```

The ZIPs are written to `dist/<Minecraft version>/`.

## License

The upright fonts come from the [official Fira Code 6.2 release](https://github.com/tonsky/FiraCode/releases/tag/6.2). Fira Code is licensed under the SIL Open Font License 1.1; the [license](OFL.txt) is also included in every ZIP.

The font setup follows [Caxton's provider documentation](https://modrinth.com/mod/caxton). The settings use Respackopts' [config format](https://gitlab.com/jfmods/respackopts/-/raw/master/docs/setup/MainConfig.md) and [resource expansion](https://gitlab.com/jfmods/respackopts/-/raw/master/docs/additional/ResourceExpansion.md).
