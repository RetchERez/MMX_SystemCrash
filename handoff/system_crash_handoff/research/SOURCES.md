# Research references

Sources identified or inspected during the prior conversation. Retrieve current contents and pin revisions locally; no third-party repository or copyrighted ROM assets are bundled. Some historical web claims were not independently verified against the ROM.

## Primary design / historical evidence
- Capcom Rockman Unity retrospective, Hayato Kaji interview (2018): https://rockmanunity.blog.jp/archives/9189663.html
- Japanese original game manual (Capcom Captown): https://captown.capcom.com/uploads/game/manual/28/MegamanX_ja_G.99433159-6637-4f73-a1fc-3a2bd3485db7.pdf
- Nintendo Wii Virtual Console X1 guide: https://www.nintendo.co.jp/wii/vc/vc_rmx/vc_rmx_08.html
- Later PSP Maverick Hunter X manual, facility/character profiles (not evidence of exact SNES behavior): https://static.capcom.com/megaman/manuals/PSP_MMMHX_Manual.pdf
- Developer interviews / diary translation: https://shmuplations.com/megamanx/
- Prerelease White City context (not planned for this mod): https://kobun20.interordi.com/2010/06/22/retro-x/

## Technical references
- X1 reference disassembly: https://github.com/MarkAlarm/MMX1-Disassembly (README is minimal, no confirmed revision)
- Split documented disassembly (Rev 0 header observed): https://github.com/AkiteruSDA/MMX1-Disassembly/tree/documentation/src
- Rev 1 randomizer, explicit stage check offsets: https://github.com/LordTony/MegaManXRandomizer/blob/master/rando.py
- MegaED X source and event layout: https://github.com/rbrummett/megaedx_v1.3
- XSharp actor mapping: https://github.com/sharivan/XSharp/blob/master/ROMExporter/MegaEDX/MMXCoreLoader.cs
- Rev 1 PC recompilation (research only; not SNES patch output): https://github.com/mstan/MegaManXSNESRecomp
- Bunker native reaction notes: https://github.com/mstan/MegaManXSNESRecomp/blob/main/docs/weapons/x1-stage-reactions.md
- Data Crystal ROM map: https://datacrystal.tcrf.net/wiki/Mega_Man_X
- Rev 1 dump metadata: https://data.spludlow.co.uk/no-intro/no-intro/Nintendo%20-%20Super%20Nintendo%20Entertainment%20System/Mega%20Man%20X%20%28USA%29%20%28Rev%201%29
- MSU-1 Rev 1 project: https://github.com/mlarouche/MegamanX-MSU1

## Stage and enemy references (secondary, verify against ROM)
- Original weakness and stage changes: https://gamefaqs.gamespot.com/snes/588479-mega-man-x/faqs/12768
- Enemy reference: https://gamefaqs.gamespot.com/snes/588479-mega-man-x/faqs/17278
- https://strategywiki.org/wiki/Mega_Man_X/Chill_Penguin
- https://strategywiki.org/wiki/Mega_Man_X/Flame_Mammoth
- https://strategywiki.org/wiki/Mega_Man_X/Spark_Mandrill
- https://strategywiki.org/wiki/Mega_Man_X/Storm_Eagle
- https://strategywiki.org/wiki/Mega_Man_X/Boomer_Kuwanger
- https://strategywiki.org/wiki/Mega_Man_X/Armored_Armadillo
- https://strategywiki.org/wiki/Mega_Man_X/Launch_Octopus
- https://strategywiki.org/wiki/Mega_Man_X/Sting_Chameleon
- Unverified bird report: https://www.mmhp.net/GameHints/MMX1.html
- X1 sprite/tile references: https://www.spriters-resource.com/snes/mmx/

## Existing hack survey
No released hack centered on exactly this expanded reaction matrix was identified in the earlier search. This is not proof of uniqueness. Randomizers retain/adjust native flags, and other projects alter levels or balance. No external hack code or assets are required for this design.
