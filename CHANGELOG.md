## [0.2.1](https://github.com/ansys/pyansys-sound/releases/tag/v0.2.1) - August 12, 2025


### Dependencies

- Fix: ``ansys-dpf-core`` version [#331](https://github.com/ansys/pyansys-sound/pull/331)

## [0.2.0](https://github.com/ansys/pyansys-sound/releases/tag/v0.2.0) - July 17, 2025


### Added

- docs: updated default image for the documentation cards page of examples 3, 4 and 5 [#82](https://github.com/ansys/pyansys-sound/pull/82)
- feat: Sound power level class and tests [#104](https://github.com/ansys/pyansys-sound/pull/104)
- feat: new indicator SpectralCentroid, with its associated tests [#150](https://github.com/ansys/pyansys-sound/pull/150)
- feat: spectrum source control for sound composer [#158](https://github.com/ansys/pyansys-sound/pull/158)
- feat: tonality DIN45681 [#161](https://github.com/ansys/pyansys-sound/pull/161)
- feat: source spectrum for sound composer [#162](https://github.com/ansys/pyansys-sound/pull/162)
- feat: sound composer's source audio [#169](https://github.com/ansys/pyansys-sound/pull/169)
- feat: sound composer's source control time [#170](https://github.com/ansys/pyansys-sound/pull/170)
- feat: source broadband noise for sound composer [#172](https://github.com/ansys/pyansys-sound/pull/172)
- feat: source broadband noise 2 parameters for sound composer [#180](https://github.com/ansys/pyansys-sound/pull/180)
- feat: source harmonics for sound composer [#184](https://github.com/ansys/pyansys-sound/pull/184)
- feat: source harmonics 2 parameters for sound composer [#186](https://github.com/ansys/pyansys-sound/pull/186)
- test: Improving `conftest.py` so that local configuration is handled [#187](https://github.com/ansys/pyansys-sound/pull/187)
- feat: filter class for sound composer (and other things) [#190](https://github.com/ansys/pyansys-sound/pull/190)
- feat: Sound Composer track [#191](https://github.com/ansys/pyansys-sound/pull/191)
- feat: improve example files handling in examples scripts [#193](https://github.com/ansys/pyansys-sound/pull/193)
- feat: Sound Composer main helper class [#200](https://github.com/ansys/pyansys-sound/pull/200)
- feat: overall level and level over time [#201](https://github.com/ansys/pyansys-sound/pull/201)
- feat: class tone_to_noise_ratio_for_orders_vs_time [#202](https://github.com/ansys/pyansys-sound/pull/202)
- feat: Aures tonality [#205](https://github.com/ansys/pyansys-sound/pull/205)
- feat: PR for orders over time [#207](https://github.com/ansys/pyansys-sound/pull/207)
- feat: Tonality ECMA418-2 [#208](https://github.com/ansys/pyansys-sound/pull/208)
- feat: tonality iso1996 2 [#209](https://github.com/ansys/pyansys-sound/pull/209)
- feat: Tonality ISO1996-2 C over time [#210](https://github.com/ansys/pyansys-sound/pull/210)
- feat: update Sharpness and Roughness classes (sharpness field type and roughness vs time) [#216](https://github.com/ansys/pyansys-sound/pull/216)
- feat: Sharpness over time [#217](https://github.com/ansys/pyansys-sound/pull/217)
- feat: sharpness DIN and sharpness DIN over time [#219](https://github.com/ansys/pyansys-sound/pull/219)
- feat: loudness ANSI S3.4 [#220](https://github.com/ansys/pyansys-sound/pull/220)
- feat: remove compatibility with fields containers in psychoacoustics package [#226](https://github.com/ansys/pyansys-sound/pull/226)
- feat: Tonality IS/TS 20065 [#239](https://github.com/ansys/pyansys-sound/pull/239)
- feat: Loudness ISO 532-2 [#244](https://github.com/ansys/pyansys-sound/pull/244)
- feat: update of example007, to include newly available psychoacoustic metrics [#246](https://github.com/ansys/pyansys-sound/pull/246)
- feat: save sound composer project [#248](https://github.com/ansys/pyansys-sound/pull/248)
- feat: Spectrum synthesis method passed as a string, instead of an integer previously [#251](https://github.com/ansys/pyansys-sound/pull/251)
- feat: Example 8 - calculate RMS, dBSPL and dBA levels [#254](https://github.com/ansys/pyansys-sound/pull/254)
- feat: Updating the supported analysis window types available for PSD/Spectrograms/Levels features [#257](https://github.com/ansys/pyansys-sound/pull/257)
- feat: example of use of PR and TNR for orders [#258](https://github.com/ansys/pyansys-sound/pull/258)
- feat: new example that calculates several tonality indicators [#259](https://github.com/ansys/pyansys-sound/pull/259)
- feat: enhancing labeler [#265](https://github.com/ansys/pyansys-sound/pull/265)
- feat: new example, showing how to load and use a Sound Composer project [#266](https://github.com/ansys/pyansys-sound/pull/266)
- feat: improve stft plot computation time [#287](https://github.com/ansys/pyansys-sound/pull/287)
- Feat: new example to demonstrate the creation of a sound composer project and its use [#300](https://github.com/ansys/pyansys-sound/pull/300)


### Changed

- chore: update CHANGELOG for v0.1.3 [#94](https://github.com/ansys/pyansys-sound/pull/94)


### Fixed

- fix: Missing BLACKMAN window type in PSD and STFT classes [#103](https://github.com/ansys/pyansys-sound/pull/103)
- fix: Updated SWL tests with latest modifs from DLL [#114](https://github.com/ansys/pyansys-sound/pull/114)
- fix: update swl operator callback [#129](https://github.com/ansys/pyansys-sound/pull/129)
- ci: ``pyvista/setup-headless-display`` started failing [#135](https://github.com/ansys/pyansys-sound/pull/135)
- fix: swl doc issue #153 [#163](https://github.com/ansys/pyansys-sound/pull/163)
- fix: remove unnecessary explicit getters [#166](https://github.com/ansys/pyansys-sound/pull/166)
- fix: spacings on CONTRIBUTORS.md file [#178](https://github.com/ansys/pyansys-sound/pull/178)
- fix: add field type in loudness ISO532-1 (stationary/time-varying) [#223](https://github.com/ansys/pyansys-sound/pull/223)
- fix: apply the same PSD parameters for TNR/PR calculation as in SAS [#224](https://github.com/ansys/pyansys-sound/pull/224)
- fix: avoid the usage of the "egg" concept [#227](https://github.com/ansys/pyansys-sound/pull/227)
- fix: Explicitly add requests package to project dependencies [#231](https://github.com/ansys/pyansys-sound/pull/231)
- fix: Wrong unit for specific loudness and specific roughness in documentation [#232](https://github.com/ansys/pyansys-sound/pull/232)
- fix: inaccurate error messages in class WriteWav [#252](https://github.com/ansys/pyansys-sound/pull/252)
- fix: update autodenoise test reference values following DPF Sound DLL update [#271](https://github.com/ansys/pyansys-sound/pull/271)
- fix: update tests following changes in DPF sound STFT [#290](https://github.com/ansys/pyansys-sound/pull/290)


### Dependencies

- build: bump pyvista from 0.44.0 to 0.44.1 [#84](https://github.com/ansys/pyansys-sound/pull/84)
- build: bump sphinx-autodoc-typehints from 2.2.2 to 2.2.3 [#85](https://github.com/ansys/pyansys-sound/pull/85)
- build: bump sphinx-gallery from 0.16.0 to 0.17.0 [#86](https://github.com/ansys/pyansys-sound/pull/86)
- build: bump pytest from 8.2.2 to 8.3.1 [#87](https://github.com/ansys/pyansys-sound/pull/87)
- build: bump sphinx from 7.4.0 to 7.4.7 [#88](https://github.com/ansys/pyansys-sound/pull/88)
- build: bump sphinx-design from 0.6.0 to 0.6.1 [#97](https://github.com/ansys/pyansys-sound/pull/97)
- build: bump ansys-dpf-core from 0.12.2 to 0.13.0 [#98](https://github.com/ansys/pyansys-sound/pull/98)
- build: bump numpydoc from 1.7.0 to 1.8.0 [#99](https://github.com/ansys/pyansys-sound/pull/99)
- build: bump trame-vtk from 2.8.9 to 2.8.10 [#100](https://github.com/ansys/pyansys-sound/pull/100)
- build: bump matplotlib from 3.8.4 to 3.9.1.post1 [#101](https://github.com/ansys/pyansys-sound/pull/101)
- build: bump sphinx from 7.4.7 to 8.0.2 [#102](https://github.com/ansys/pyansys-sound/pull/102)
- build: bump sphinx-gallery from 0.17.0 to 0.17.1 [#105](https://github.com/ansys/pyansys-sound/pull/105)
- build: bump pytest from 8.3.1 to 8.3.2 [#106](https://github.com/ansys/pyansys-sound/pull/106)
- build: bump ansys-sphinx-theme from 0.16.6 to 1.0.7 [#107](https://github.com/ansys/pyansys-sound/pull/107)
- build: bump regex from 2024.5.15 to 2024.7.24 [#108](https://github.com/ansys/pyansys-sound/pull/108)
- build: bump matplotlib from 3.9.1.post1 to 3.9.2 [#109](https://github.com/ansys/pyansys-sound/pull/109)
- build: bump sphinx-autodoc-typehints from 2.2.3 to 2.3.0 [#110](https://github.com/ansys/pyansys-sound/pull/110)
- build: bump ansys-sphinx-theme from 1.0.7 to 1.0.8 [#115](https://github.com/ansys/pyansys-sound/pull/115)
- build: bump sphinx-autodoc-typehints from 2.3.0 to 2.4.0 [#116](https://github.com/ansys/pyansys-sound/pull/116)
- build: bump sphinx-autobuild from 2024.4.16 to 2024.9.3 [#118](https://github.com/ansys/pyansys-sound/pull/118)
- build: bump regex from 2024.7.24 to 2024.9.11 [#120](https://github.com/ansys/pyansys-sound/pull/120)
- build: bump sphinx-autodoc-typehints from 2.4.0 to 2.4.1 [#121](https://github.com/ansys/pyansys-sound/pull/121)
- build: bump pytest from 8.3.2 to 8.3.3 [#122](https://github.com/ansys/pyansys-sound/pull/122)
- build: bump sphinx-autobuild from 2024.9.3 to 2024.9.19 [#123](https://github.com/ansys/pyansys-sound/pull/123)
- build: bump sphinx-autodoc-typehints from 2.4.1 to 2.4.4 [#124](https://github.com/ansys/pyansys-sound/pull/124)
- build: bump platformdirs from 4.2.2 to 4.3.6 [#125](https://github.com/ansys/pyansys-sound/pull/125)
- build: bump ansys-sphinx-theme from 1.0.8 to 1.0.11 [#126](https://github.com/ansys/pyansys-sound/pull/126)
- build: bump trame from 3.6.3 to 3.6.5 [#127](https://github.com/ansys/pyansys-sound/pull/127)
- build: bump sphinx-autobuild from 2024.9.19 to 2024.10.3 [#133](https://github.com/ansys/pyansys-sound/pull/133)
- build: bump ansys-sphinx-theme from 1.0.11 to 1.1.2 [#134](https://github.com/ansys/pyansys-sound/pull/134)
- build: bump sphinx-gallery from 0.17.1 to 0.18.0 [#140](https://github.com/ansys/pyansys-sound/pull/140)
- build: bump pypandoc from 1.13 to 1.14 [#141](https://github.com/ansys/pyansys-sound/pull/141)
- build: bump ansys-sphinx-theme from 1.1.2 to 1.1.3 [#142](https://github.com/ansys/pyansys-sound/pull/142)
- build: bump sphinx from 8.0.2 to 8.1.3 [#143](https://github.com/ansys/pyansys-sound/pull/143)
- build: bump sphinx-autodoc-typehints from 2.4.4 to 2.5.0 [#144](https://github.com/ansys/pyansys-sound/pull/144)
- build: bump ansys-sphinx-theme from 1.1.3 to 1.1.6 [#146](https://github.com/ansys/pyansys-sound/pull/146)
- build: bump trame-vtk from 2.8.10 to 2.8.11 [#147](https://github.com/ansys/pyansys-sound/pull/147)
- build: bump trame from 3.6.5 to 3.7.0 [#148](https://github.com/ansys/pyansys-sound/pull/148)
- build: bump pytest-cov from 5.0.0 to 6.0.0 [#151](https://github.com/ansys/pyansys-sound/pull/151)
- build: bump ansys-sphinx-theme from 1.1.6 to 1.2.0 [#152](https://github.com/ansys/pyansys-sound/pull/152)
- build: bump ansys-dpf-core from 0.13.0 to 0.13.2 [#154](https://github.com/ansys/pyansys-sound/pull/154)
- build: bump regex from 2024.9.11 to 2024.11.6 [#155](https://github.com/ansys/pyansys-sound/pull/155)
- build: bump trame-vtk from 2.8.11 to 2.8.12 [#156](https://github.com/ansys/pyansys-sound/pull/156)
- build: bump ansys-sphinx-theme from 1.2.0 to 1.2.1 [#159](https://github.com/ansys/pyansys-sound/pull/159)
- build: bump ansys-sphinx-theme from 1.2.1 to 1.2.2 [#168](https://github.com/ansys/pyansys-sound/pull/168)
- build: bump pyvista from 0.44.1 to 0.44.2 [#173](https://github.com/ansys/pyansys-sound/pull/173)
- build: bump ansys-dpf-core from 0.13.2 to 0.13.3 [#174](https://github.com/ansys/pyansys-sound/pull/174)
- build: bump matplotlib from 3.9.2 to 3.9.3 [#175](https://github.com/ansys/pyansys-sound/pull/175)
- build: bump pytest from 8.3.3 to 8.3.4 [#176](https://github.com/ansys/pyansys-sound/pull/176)
- build: bump matplotlib from 3.9.3 to 3.10.0 [#192](https://github.com/ansys/pyansys-sound/pull/192)
- build: bump ansys-sphinx-theme from 1.2.2 to 1.2.4 [#194](https://github.com/ansys/pyansys-sound/pull/194)
- build: bump trame from 3.7.0 to 3.7.6 [#198](https://github.com/ansys/pyansys-sound/pull/198)
- build: bump sphinx-autodoc-typehints from 2.5.0 to 3.0.0 [#199](https://github.com/ansys/pyansys-sound/pull/199)
- build: bump pypandoc from 1.14 to 1.15 [#204](https://github.com/ansys/pyansys-sound/pull/204)
- build: bump ansys-dpf-core from 0.13.3 to 0.13.4 [#218](https://github.com/ansys/pyansys-sound/pull/218)
- build: bump ansys-sphinx-theme from 1.2.4 to 1.3.1 [#230](https://github.com/ansys/pyansys-sound/pull/230)
- build: bump sphinx-gallery from 0.18.0 to 0.19.0 [#233](https://github.com/ansys/pyansys-sound/pull/233)
- build: bump ansys-sphinx-theme from 1.3.1 to 1.3.2 [#235](https://github.com/ansys/pyansys-sound/pull/235)
- build: bump sphinx-autodoc-typehints from 3.0.0 to 3.1.0 [#236](https://github.com/ansys/pyansys-sound/pull/236)
- build: bump sphinx from 8.1.3 to 8.2.1 [#237](https://github.com/ansys/pyansys-sound/pull/237)
- build: bump matplotlib from 3.10.0 to 3.10.1 [#240](https://github.com/ansys/pyansys-sound/pull/240)
- build: bump pytest from 8.3.4 to 8.3.5 [#241](https://github.com/ansys/pyansys-sound/pull/241)
- build: bump sphinx from 8.2.1 to 8.2.3 [#242](https://github.com/ansys/pyansys-sound/pull/242)
- build: bump trame from 3.7.6 to 3.8.1 [#247](https://github.com/ansys/pyansys-sound/pull/247)
- build: bump ansys-sphinx-theme from 1.3.2 to 1.3.3 [#253](https://github.com/ansys/pyansys-sound/pull/253)
- build: bump platformdirs from 4.3.6 to 4.3.7 [#255](https://github.com/ansys/pyansys-sound/pull/255)
- build: bump ansys-sphinx-theme from 1.3.3 to 1.4.2 [#261](https://github.com/ansys/pyansys-sound/pull/261)
- build: bump pytest-cov from 6.0.0 to 6.1.1 [#263](https://github.com/ansys/pyansys-sound/pull/263)
- build: bump trame from 3.8.1 to 3.8.2 [#268](https://github.com/ansys/pyansys-sound/pull/268)
- build: bump pyvista from 0.44.2 to 0.45.0 [#274](https://github.com/ansys/pyansys-sound/pull/274)
- build: bump trame from 3.8.2 to 3.9.0 [#275](https://github.com/ansys/pyansys-sound/pull/275)
- build: bump platformdirs from 4.3.7 to 4.3.8 [#277](https://github.com/ansys/pyansys-sound/pull/277)
- build: bump ansys-sphinx-theme from 1.4.2 to 1.4.4 [#278](https://github.com/ansys/pyansys-sound/pull/278)
- build: bump matplotlib from 3.10.1 to 3.10.3 [#279](https://github.com/ansys/pyansys-sound/pull/279)
- build: bump pyvista from 0.45.0 to 0.45.1 [#280](https://github.com/ansys/pyansys-sound/pull/280)
- build: bump pyvista from 0.45.1 to 0.45.2 [#282](https://github.com/ansys/pyansys-sound/pull/282)
- build: bump trame from 3.9.0 to 3.10.1 [#285](https://github.com/ansys/pyansys-sound/pull/285)
- build: bump ansys-sphinx-theme from 1.4.4 to 1.5.0 [#286](https://github.com/ansys/pyansys-sound/pull/286)
- build: bump ansys-sphinx-theme from 1.5.0 to 1.5.2 [#292](https://github.com/ansys/pyansys-sound/pull/292)
- build: bump trame-vtk from 2.8.12 to 2.8.17 [#293](https://github.com/ansys/pyansys-sound/pull/293)
- build: bump trame from 3.10.1 to 3.10.2 [#294](https://github.com/ansys/pyansys-sound/pull/294)
- build: bump pytest from 8.3.5 to 8.4.0 [#295](https://github.com/ansys/pyansys-sound/pull/295)


### Miscellaneous

- build: [pre-commit.ci] pre-commit autoupdate [#81](https://github.com/ansys/pyansys-sound/pull/81), [#137](https://github.com/ansys/pyansys-sound/pull/137)
- docs: update examples card images [#83](https://github.com/ansys/pyansys-sound/pull/83)
- doc: adding missing doc for PSD [#95](https://github.com/ansys/pyansys-sound/pull/95)
- chore: pre-commit autoupdate [#145](https://github.com/ansys/pyansys-sound/pull/145)
- chore: [pre-commit.ci] pre-commit autoupdate [#157](https://github.com/ansys/pyansys-sound/pull/157), [#179](https://github.com/ansys/pyansys-sound/pull/179), [#206](https://github.com/ansys/pyansys-sound/pull/206), [#221](https://github.com/ansys/pyansys-sound/pull/221), [#225](https://github.com/ansys/pyansys-sound/pull/225), [#234](https://github.com/ansys/pyansys-sound/pull/234), [#238](https://github.com/ansys/pyansys-sound/pull/238), [#245](https://github.com/ansys/pyansys-sound/pull/245), [#262](https://github.com/ansys/pyansys-sound/pull/262), [#270](https://github.com/ansys/pyansys-sound/pull/270)
- fix: replace mutable empty list by None in Filter class constructor [#214](https://github.com/ansys/pyansys-sound/pull/214)
- Ci: bump ansys/actions from 9.0.13 to 10.0.10 in the actions group [#291](https://github.com/ansys/pyansys-sound/pull/291)
- Ci: bump ansys/actions from 10.0.10 to 10.0.11 in the actions group [#298](https://github.com/ansys/pyansys-sound/pull/298), [#303](https://github.com/ansys/pyansys-sound/pull/303)
- Build: bump pytest-cov from 6.1.1 to 6.2.1 [#299](https://github.com/ansys/pyansys-sound/pull/299)
- Feat: use field units instead of hard-coded units [#301](https://github.com/ansys/pyansys-sound/pull/301)
- Build: bump pytest from 8.4.0 to 8.4.1 [#302](https://github.com/ansys/pyansys-sound/pull/302)
- Chore: [pre-commit.ci] pre-commit autoupdate [#304](https://github.com/ansys/pyansys-sound/pull/304), [#314](https://github.com/ansys/pyansys-sound/pull/314)
- Build: bump numpydoc from 1.8.0 to 1.9.0 [#306](https://github.com/ansys/pyansys-sound/pull/306)
- Build: bump trame-vtk from 2.8.17 to 2.9.0 [#307](https://github.com/ansys/pyansys-sound/pull/307)
- Build: bump vtk from 9.3.1 to 9.4.2 [#308](https://github.com/ansys/pyansys-sound/pull/308)
- Ci: bump ansys/actions from 10.0.11 to 10.0.12 in the actions group [#309](https://github.com/ansys/pyansys-sound/pull/309)
- Test: checking the dpf server version in new features, and in unit tests related to bug fixed in 2026 r1 [#310](https://github.com/ansys/pyansys-sound/pull/310)
- Build: bump ansys-sphinx-theme from 1.5.2 to 1.5.3 [#313](https://github.com/ansys/pyansys-sound/pull/313)
- Ci: run ci/cd tests on all past official releases, in addition to the latest package [#316](https://github.com/ansys/pyansys-sound/pull/316)


### Documentation

- docs: add user_agent to check Ansys links [#112](https://github.com/ansys/pyansys-sound/pull/112)
- docs: linkcheck ignore ansys urls [#113](https://github.com/ansys/pyansys-sound/pull/113)
- ci: bump ansys/actions from 7 to 8 in the actions group [#136](https://github.com/ansys/pyansys-sound/pull/136)
- docs: fix extra ``:`` in API doc and add ``favicon`` in ``conf.py`` [#164](https://github.com/ansys/pyansys-sound/pull/164)
- docs: sort out doc and type hints for numpy arrays [#171](https://github.com/ansys/pyansys-sound/pull/171)
- chore: update license year [#197](https://github.com/ansys/pyansys-sound/pull/197)
- docs: documentation review of the recent Sound Composer and Psychoacoustic new features [#243](https://github.com/ansys/pyansys-sound/pull/243)
- docs: Documentation review for all of PyAnsys Sound [#256](https://github.com/ansys/pyansys-sound/pull/256)


### Maintenance

- ci: bump ansys/actions from 6 to 7 in the actions group [#96](https://github.com/ansys/pyansys-sound/pull/96)
- maint: Updating AUTHORS and CONTRIBUTORS.md [#138](https://github.com/ansys/pyansys-sound/pull/138)
- ci: deleting docker images from cicd [#165](https://github.com/ansys/pyansys-sound/pull/165)
- ci: bump the actions group across 1 directory with 2 updates [#177](https://github.com/ansys/pyansys-sound/pull/177), [#276](https://github.com/ansys/pyansys-sound/pull/276)
- chore: supporting Python 3.13 and dropping support for Python 3.9 [#185](https://github.com/ansys/pyansys-sound/pull/185)
- ci: switch pydpfcore dependency to dev version [#222](https://github.com/ansys/pyansys-sound/pull/222)
- ci: Changing CI call to docker container only for tests [#249](https://github.com/ansys/pyansys-sound/pull/249)
- docs: Update ``CONTRIBUTORS.md`` with the latest contributors [#267](https://github.com/ansys/pyansys-sound/pull/267)
- ci: bump ansys/actions from 8 to 9 in the actions group [#269](https://github.com/ansys/pyansys-sound/pull/269)
- ci: fix tcl/tk random errors by specifying headless matplotlib backend [#281](https://github.com/ansys/pyansys-sound/pull/281)
- ci: fix buildhouse issue [#283](https://github.com/ansys/pyansys-sound/pull/283)
- ci: bump ansys/actions from 9.0.9 to 9.0.13 in the actions group [#284](https://github.com/ansys/pyansys-sound/pull/284)
- Feat: old docker image housekeeping [#296](https://github.com/ansys/pyansys-sound/pull/296)


### Test

- Feat: the function connect_to_or_start_server now returns the licensecontext instead of storing it as a member of the server object [#288](https://github.com/ansys/pyansys-sound/pull/288)
- Feat: use in-process server by default when using local server [#289](https://github.com/ansys/pyansys-sound/pull/289)

## [0.1.3](https://github.com/ansys/pyansys-sound/releases/tag/v0.1.3) - 2024-08-08


### Added

- feat: Add a new helper for the power spectral density operator (psd) in PyAnsys Sound [#67](https://github.com/ansys/pyansys-sound/pull/67)


### Changed

- chore: update CHANGELOG for v0.1.2 [#79](https://github.com/ansys/pyansys-sound/pull/79)


### Fixed

- fix: fixed a malfunction of the functions to download sample files used in examples [#93](https://github.com/ansys/pyansys-sound/pull/93)


### Dependencies

- build: bump sphinx from 7.3.7 to 7.4.0 [#80](https://github.com/ansys/pyansys-sound/pull/80)

## [0.1.2](https://github.com/ansys/pyansys-sound/releases/tag/v0.1.2) - 2024-07-11


### Changed

- chore: update CHANGELOG for v0.1.1 [#77](https://github.com/ansys/pyansys-sound/pull/77)
- build: using `flit_core` as build-system [#78](https://github.com/ansys/pyansys-sound/pull/78)

## [0.1.1](https://github.com/ansys/pyansys-sound/releases/tag/v0.1.1) - 2024-07-10


### Changed

- chore: update CHANGELOG for v0.1.0 [#75](https://github.com/ansys/pyansys-sound/pull/75)

## [0.1.0](https://github.com/ansys/pyansys-sound/releases/tag/v0.1.0) - 2024-07-09


### Added

- chore: adding check-vulnerabilities-action [#37](https://github.com/ansys/pyansys-sound/pull/37)
- feat: enhancements items to work for official release [#39](https://github.com/ansys/pyansys-sound/pull/39)
- feat: Added deploy changelog action to CI/CD + Updating pyproject.toml [#46](https://github.com/ansys/pyansys-sound/pull/46)


### Changed

- ci: bump the actions group with 2 updates [#45](https://github.com/ansys/pyansys-sound/pull/45)


### Fixed

- fix: proper conventional commit style [#47](https://github.com/ansys/pyansys-sound/pull/47)
- fix: cyclic imports [#52](https://github.com/ansys/pyansys-sound/pull/52)
- chore: pre-release tasks [#68](https://github.com/ansys/pyansys-sound/pull/68)
- fix: dependencies [#69](https://github.com/ansys/pyansys-sound/pull/69)
- fix: ``test_pkg_version`` test [#71](https://github.com/ansys/pyansys-sound/pull/71)
- fix: version in ``pyproject.toml`` [#72](https://github.com/ansys/pyansys-sound/pull/72)


### Dependencies

- build: bump pytest from 8.2.1 to 8.2.2 [#40](https://github.com/ansys/pyansys-sound/pull/40)
- build: bump trame-vtk from 2.8.8 to 2.8.9 [#41](https://github.com/ansys/pyansys-sound/pull/41)
- build: bump sphinx-autodoc-typehints from 2.1.0 to 2.1.1 [#42](https://github.com/ansys/pyansys-sound/pull/42)
- build: bump sphinx-design from 0.5.0 to 0.6.0 [#44](https://github.com/ansys/pyansys-sound/pull/44)
- build: bump sphinx-autodoc-typehints from 2.1.1 to 2.2.2 [#55](https://github.com/ansys/pyansys-sound/pull/55)
- build: bump pyvista from 0.43.8 to 0.43.10 [#56](https://github.com/ansys/pyansys-sound/pull/56)
- build: bump trame from 3.6.1 to 3.6.3 [#57](https://github.com/ansys/pyansys-sound/pull/57)
- build: bump pypandoc from 1.12.0 to 1.13 [#58](https://github.com/ansys/pyansys-sound/pull/58)
- build: bump platformdirs from 4.2.0 to 4.2.2 [#59](https://github.com/ansys/pyansys-sound/pull/59)
- build: bump vtk from 9.3.0 to 9.3.1 [#60](https://github.com/ansys/pyansys-sound/pull/60)
- build: bump ansys-dpf-core from 0.12.1 to 0.12.2 [#61](https://github.com/ansys/pyansys-sound/pull/61)
- build: bump ansys-sphinx-theme from 0.16.4 to 0.16.6 [#62](https://github.com/ansys/pyansys-sound/pull/62)
- build: bump sphinx-gallery from 0.15.0 to 0.16.0 [#63](https://github.com/ansys/pyansys-sound/pull/63)


### Miscellaneous

- docs: overall doc review [#48](https://github.com/ansys/pyansys-sound/pull/48), [#49](https://github.com/ansys/pyansys-sound/pull/49), [#50](https://github.com/ansys/pyansys-sound/pull/50), [#53](https://github.com/ansys/pyansys-sound/pull/53)
- docs: final edits based on skimming last HTML artifact [#54](https://github.com/ansys/pyansys-sound/pull/54)

# CHANGELOG

This project uses [towncrier](https://towncrier.readthedocs.io/) to generate changelogs. You can see the changes for the upcoming release in <https://github.com/ansys/pyansys-sound/tree/main/changelog.d/>.

<!-- towncrier release notes start -->