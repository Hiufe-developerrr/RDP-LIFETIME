# Bizon Z050 Super z hederem 4,20 m – model 3D (Blender → FS25)

Model klasycznego polskiego kombajnu **Bizon Z050 Super** (FMŻ Bizon, 1973–76) z hederem zbożowym
**4,20 m**. Całość zbudowano skryptami Pythona wysyłanymi do działającego Blendera przez serwer
**MCP for Blender** (`execute_blender_code`, socket `127.0.0.1:9876`). Siatki, łączenie obiektów,
materiały, UV, wypalanie tekstur i eksport też wykonują te skrypty.

![Bizon Z050 Super – widok z przodu z lewej](renders/front_left.jpg)

## Zawartość

| Ścieżka | Opis |
| --- | --- |
| `blend/bizon_z050_super.blend` | Scena Blendera 4.2 LTS: kombajn, heder, kolizje, światło i kamery do renderu |
| `export/bizon_z050_super_fs25.fbx` | Eksport z wypalonymi materiałami atlasowymi (oś Y do góry, przód +Z jak w GIANTS) |
| `textures/` | Wypalone atlasy `*_diffuse.png`, `*_normal.png`, `*_specular.png` |
| `renders/` | Rendery Cycles z proceduralnymi materiałami |
| `scripts/` | Skrypty budujące model przez MCP (`lib.py` jest doklejany do każdego wywołania) |

## Wymiary i proporcje

Przyjęte według danych technicznych Z050 Super i proporcji ze zdjęć Z050/Z056:

- długość z hederem ok. 8,2 m, szerokość bez hedera 3,15 m, wysokość do daszku 3,63 m;
- koła przednie (napędowe) **18.4-30**, bieżnik R-1 w jodełkę, kremowe felgi W16L-30 z otworami;
- koła tylne (skrętne) **10.00-15**, bieżnik żeberkowy, oś wahliwa ze zwrotnicami i drążkiem;
- otwarte stanowisko operatora z daszkiem na czterech słupkach (kremowy wierzch, szary podsufit),
  poręcze, fotel, kolumna kierownicy z zegarami, dźwignie, pedały, lusterka, reflektory robocze, kogut;
- zbiornik ziarna z pokrywami i wziernikiem, komora silnika z żaluzjami chłodnicy (lewa strona),
  tłumik i komin wydechu, filtr powietrza z cyklonem, podnośnik ziarna i przekładnie pasowe (prawa strona);
- rura wysypowa po lewej stronie w pozycji transportowej, wypust z gumowym rękawem, kołyska oparcia;
- tył: fartuch słomy, lampy zespolone, trójkąt wyróżniający pojazd wolnobieżny, zaczep;
- znaki: tarcza „fmż”, tabliczki „BIZON”, napis „super Z050”;
- heder 4,20 m: koryto z otworem podajnika, ściany boczne, rozdzielacze, belka nożowa z **55 palcami**
  (podziałka 76,2 mm) i listwą nożową, ślimak z przeciwbieżnymi zwojami i palcami, motowidło palcowe
  Ø 1,0 m (6 listew, zęby sprężynowe) na ramionach z siłownikami, napęd pasowy i łańcuchowy.

## Przygotowanie pod Farming Simulator 25

- Skala 1 jednostka = 1 m, model skierowany przodem do **−Y** w Blenderze (po eksporcie +Z w GIANTS).
- Modyfikatory (fazki, weighted normals) są zastosowane. Normalne niestandardowe dają ostre krawędzie i gładkie fazki.
- Statyczne części złączone w `bizonZ050_body` i `header420_body`, szkła i klosze w `bizonZ050_lights`.
- Hierarchia z pivotami w miejscach obrotu:

```
bizonZ050                      header420 (punkt zaczepu na przenośniku)
├─ bizonZ050_body              ├─ header420_body
├─ bizonZ050_lights            ├─ knife            (ruch wzdłuż X)
├─ feederHouse  (oś podnoszenia)├─ auger → augerMesh (obrót X)
├─ feederLiftCylinders         └─ reelArms (pivot ramion) → reelArmsMesh
├─ steeringWheel (lokalna oś Z = kolumna)          └─ reel → reelMesh (obrót X)
├─ pipe (obrót Z) → pipeTube
├─ frontAxle → wheelFrontLeft/Right → tire*, rim*, hub*
└─ rearAxle (wahliwa, obrót Y) → steeringKnuckleRearLeft/Right → knuckle*, wheelRear* → tire*, rim*
   └─ rearAxleTieRod
```

- Proste bryły kolizji w kolekcji `Z050_collision`.
- UV: trzy atlasy bez nakładania się UV: `bizonZ050` (2048²), `header420` (2048²) i `bizonZ050_tires` (1024²).
- Tekstury: `*_diffuse` (sRGB), `*_normal` (tangent, konwencja OpenGL Y+) oraz
  `*_specular` spakowany jako **R = gładkość (1 − roughness), G = metaliczność, B = AO**.
  Sprawdź ten układ kanałów i kierunek zielonego kanału normal mapy z szablonem shadera, którego
  używasz w FS25, i w razie potrzeby przepakuj kanały. Pliki DDS utworzysz narzędziem GIANTS Texture Tool.

### Eksport do i3d

1. Otwórz `blend/bizon_z050_super.blend` w Blenderze **4.2 lub 4.3** (tych wersji wymaga GIANTS I3D Exporter v10).
2. W edytorze tekstu uruchom `fs25_switch_materials.py` (`MODE = "BAKED"`). Siatki dostaną wtedy
   wypalone materiały atlasowe. Z `MODE = "PROCEDURAL"` wracają materiały proceduralne.
3. Wyeksportuj kolekcje `Z050_combine` i `Z050_header420` exporterem GIANTS. Następnie przypisz
   `vehicleShader.xml`, oznacz kolizje i ustaw wheels/attacherJoints w XML pojazdu. Heder to w FS osobny pojazd (cutter).

## Materiały PBR i zużycie

W scenie przypisane są proceduralne materiały PBR (`Z050_paint_red`, `Z050_paint_cream`,
`Z050_paint_gray`, `Z050_metal_dark`, `Z050_steel`, `Z050_rubber_tire` i inne) oparte na grupie
węzłów `Z050_Weathering`. Grupa daje: wyblakły od słońca lakier (łososiowe plamy na górnych
powierzchniach), kurz i brud w zagłębieniach i nisko przy ziemi, odpryski na krawędziach z podkładem,
gołą blachą i rdzą, rdzawe i brudne zacieki oraz zmienną chropowatość. Maski krawędzi i AO działają
w Cycles, dlatego wygląd do gry jest wypalony w atlasy.

## Odtworzenie modelu przez MCP

Wymagania: Blender 4.2 z włączonym dodatkiem MCP for Blender (serwer na `127.0.0.1:9876`) oraz
`uv tool install mcp-for-blender`.

```bash
cd bizon_z050/scripts
export BLENDER_HOST=127.0.0.1 BLENDER_PORT=9876
PY=~/.local/share/uv/tools/mcp-for-blender/bin/python
$PY mcp_client.py --lib lib.py --code 00_scene.py --code 01_materials.py --code 02_chassis.py \
    --code 03_wheels.py --code 04_operator.py --code 05_details.py --code 06_header.py \
    --code 07_finalize.py --code 08_render_setup.py
$PY mcp_client.py --lib lib.py --code 09_bake.py   # wypalanie w tle, postęp: textures/bake_status.txt
$PY mcp_client.py --lib lib.py --code 10_export.py # FBX + zapis .blend
```

Skrypty zapisują pliki w `/tmp/hoplite/workspace/bizon_z050`. Przy innej lokalizacji zmień stałe
`OUT`/`BASE` w `09_bake.py`, `10_export.py` i `render_job.py`.
