**Lighting for auto-captured cement-bag SKU recognition**

**Archived on 11 October 2026 at the user's request.** Additional lighting is removed from the current project experiment plan. This file preserves earlier reference research only; its configurations and hardware recommendations are deferred. The active plan in `cement-bag-recognition-research.md` tests models and software with the current camera and lighting setup.

Research checked on 11 October 2026. This supplements the recognition architecture review. The recommendations below are proposed experiments for the supplied top-down bag images; they are not measured results from this production line.

**Recommendation**

Start by comparing two large opposing diffused white LED sources with a diffuse tunnel or dome-style arrangement covering the full bag. Keep the camera approximately perpendicular to the conveyor, reduce ambient-light variation with a short inspection hood, and set exposure from the permitted motion blur. Use synchronized illumination when the camera supports reliable strobe timing; otherwise use stable continuous illumination. This recommendation combines general illumination research with engineering judgment about the large, wrinkled, printed surface in the samples.

There is no verified universal cement-bag setting such as a particular lux level, color temperature, angle, or lamp wattage. In the sources reviewed, no comparative study established the best combination for this specific 40-SKU, artwork-gallery recognition task. The most relevant studies address illumination geometry, field uniformity, recognition under spectral changes, and systematic lighting evaluation. Several full texts are subscription-limited, so summaries use accessible publisher abstracts, metadata, and tables where available; numerical accuracy claims are not inferred.

**Relevant papers**

1. **Wu and Gao (2018), LED light design method for high contrast and uniform illumination imaging in machine vision. Applied Optics 57(7), 1694-1704. DOI: 10.1364/AO.57.001694.**

   Optimizes contrast using surface properties and lighting direction while preserving uniformity under non-normal illumination. Use it to justify testing angle and diffusion together rather than merely increasing brightness. The paper is general machine-vision illumination design, not a cement-SKU benchmark. [Publisher abstract](https://opg.optica.org/ao/abstract.cfm?uri=ao-57-7-1694).

2. **Zhang, Peng, Luo, and Yu (2020), Rectangular illumination method using LED arrays for machine vision. Applied Optics 59(11), 3518-3525. DOI: 10.1364/AO.384833.**

   Models illumination of a rectangular target, optimizes source structure with a genetic algorithm, and validates uniformity experimentally. Especially relevant to covering an entire bag panel. Map illumination across the bag footprint and expected height range; a bright center alone is insufficient. Its experimental dimensions and illuminance should not be treated as a specification for this conveyor. [Publisher abstract and accessible tables](https://opg.optica.org/ao/abstract.cfm?uri=ao-59-11-3518).

3. **Han, Park, and Kim (2026 issue; available online in 2025), Design and optimization of multi-angle dome-shaped LED lighting system. Journal of Engineering Research 14(1), 266-277. DOI: 10.1016/j.jer.2025.05.002.**

   Designs multiple LED layers and illumination angles for uniform surface imaging, including bright-field and dark-field configurations. The accessible abstract describes optical simulations and validation with complex structures. Use its geometry ideas for a diffuse tunnel or dome comparison, but do not assume its conclusions establish conveyor throughput or printed-bag recognition accuracy. [Publisher](https://www.sciencedirect.com/science/article/pii/S2307187725000537), [authors' university record](https://yonsei.elsevierpure.com/en/publications/design-and-optimization-of-multi-angle-dome-shaped-led-lighting-s/).

4. **Singh and Desai (2025), Systematic approach determining lighting arrangement for vision-based in-line inspection of axisymmetric metallic components. Measurement, article 118134. DOI: 10.1016/j.measurement.2025.118134.**

   Compares lighting arrangements using image assessment and downstream CNN defect detection, finding value in diffuse, uniform illumination. The strongest transferable contribution is the evaluation procedure: select lighting by task performance. Its objects are reflective metallic components, so the winning arrangement cannot be assumed to be optimal for paper or woven bags. [Publisher](https://www.sciencedirect.com/science/article/pii/S0263224125014939).

5. **Ren, Fang, Yan, and Wu (online 2021; issue 2022), State of the Art in Defect Detection Based on Machine Vision. International Journal of Precision Engineering and Manufacturing-Green Technology 9, 661-691. DOI: 10.1007/s40684-021-00343-6.**

   Open-access review covering optical illumination, image acquisition, processing, and learned inspection. Use its optical-illumination discussion to distinguish lighting intended to reveal surface defects from lighting intended to retain printed appearance. It is a broad review rather than a comparative cement-bag recognition experiment. [Full article](https://link.springer.com/article/10.1007/s40684-021-00343-6).

6. **Vriesenga et al. (1995), Colored Illumination for Enhancing Discriminability in Machine Vision. Journal of Visual Communication and Image Representation 6(3), 244-255. DOI: 10.1006/jvci.1995.1021.**

   Designs illumination spectra using object reflectance and camera response to improve RGB separability. Relevant to bags distinguished by ink color. It supports selecting spectra experimentally; it does not establish that one particular white color temperature is universally best. [Publisher abstract](https://www.sciencedirect.com/science/article/pii/S1047320385710218/pdf?md5=b74e9dd587e3edda1845a21bac459feb&pid=1-s2.0-S1047320385710218-main.pdf).

7. **Zhang et al. (2023 preprint), Enhancing the machine vision performance with multi-spectral light sources. arXiv:2311.06276.**

   Compares 35 spectral settings using colored pencils and AlexNet/VGG19. Some non-white spectra perform better than white illumination in that experiment. The evaluation uses proxy ImageNet labels selected by human judgment because pencil is absent from the training classes; it is not fine-grained product recognition. Treat this as exploratory motivation to test spectrum, not strong evidence for buying multispectral hardware. [Full preprint](https://arxiv.org/html/2311.06276v1).

**Practical technical resources**

- **Edmund Optics, Successful Light Polarization Techniques.** Shows crossed polarizers on illumination and the camera lens for reducing reflective hot spots. Polarization reduces transmitted light, so compare glare reduction against noise and the required exposure. Useful if coated or laminated bags reflect strongly; not automatically beneficial for already dim matte surfaces. [Application note](https://www.edmundoptics.com/knowledge-center/application-notes/illumination/successful-light-polarization-techniques/).
- **Basler, Global Shutter, Rolling Shutter - Functionality and Characteristics of Two Exposure Methods, 2018.** Explains motion blur, row-by-row distortion, and flash timing. A global shutter does not eliminate blur caused by excessive exposure. [Manufacturer white paper](https://assets-ctf.baslerweb.com/dg51pdwahxgw/7ntd9P0LbEeEmxKj6Q6J1h/cb845234f745dddab95f3ee64994dd7d/BAS1401_White_Paper_Rolling_Shutter.pdf).
- **Basler, Light Control product documentation.** Details continuous and strobe modes, exposure synchronization, and rolling-shutter flash windows. Parameters are product-specific, but the timing principles are transferable. Automatic file capture/upload does not imply hardware strobe support: synchronization must happen at the camera exposure. [Official documentation](https://docs.baslerweb.com/light-control).
- **Ohno (2005), Spectral Design Considerations for White LED Color Rendering. Optical Engineering 44.** Background on LED spectral design and color rendering. Human color-rendering indices are useful procurement descriptors, but they do not replace testing with the actual camera and bag inks. [NIST publication record and paper link](https://www.nist.gov/publications/spectral-design-considerations-white-led-color-rendering).
- **Basler / Irida Labs cement-sack inspection case study.** Describes inspection under changing light, excessive dust, dirt, and vibration. Useful evidence that the environment matters; it does not disclose a comparative optimal-lighting recipe. [Manufacturer case study](https://www.baslerweb.com/en-sg/use-cases/irida-labs-error-detection-cement/).

**Starting configurations to test**

| Component | Proposed starting experiment | Purpose |
|---|---|---|
| Camera position | Approximately perpendicular to the conveyor; fixed framing | Stable printed-panel scale and geometry |
| Main lighting | Two opposing large diffused white LED sources, then a diffuse tunnel/dome alternative | Whole-panel illumination with reduced hard fold shadows |
| Light angles | Compare 30, 45, and 60 degrees above the conveyor plane | Determine sensitivity to texture, folds, glare, and edge darkness |
| Spectrum | Stable broad-spectrum neutral white first; roughly 5000 K is a candidate, not a proven optimum | Preserve useful color cues for artwork matching |
| Color calibration | Fixed white balance calibrated under the installed light; gray/color reference captures | Reduce avoidable camera-to-artwork color shifts |
| Exposure/gain | Choose a motion-safe exposure first, then supply enough illumination at low fixed gain | Balance blur against noise |
| Timing | Compare stable continuous illumination and camera-synchronized strobe when supported | Repeatable exposure and motion freezing |
| Glare control | Polarizers off versus crossed polarizers when hot spots actually occur | Measure benefit versus light loss |
| Ambient control | Short hood/shroud around the inspection region | Reduce shift and daylight variation |
| Dust | Compare clean and realistically contaminated protective windows and light diffusers | Quantify degradation and maintenance sensitivity |

The angles and approximate color temperature are an initial experiment grid proposed for this project. The papers do not certify them as the best cement-bag settings. A diffuser can reduce light reaching the bag, and polarizers reduce it further; measure usable print detail at the required exposure after adding either.

Prefer white-light color capture initially because the current architecture compares RGB photographs with colored artwork. Monochromatic or near-infrared illumination may be useful for a separate counting or code-reading view, but changing to them can remove visible-color distinctions and change ink contrast. Their value must be established on the actual SKU set.

SKU recognition benefits from repeatable printed appearance. Grazing illumination is worth testing separately for tears or surface damage, but it can emphasize harmless wrinkles and texture. If recognition and defects need incompatible lighting, compare two triggered exposures or separate views, with reliable association to the same physical bag.

**Calculate exposure from conveyor speed**

For locally approximately planar motion, let `s` be object-plane millimeters per image pixel along the movement direction, `v` the conveyor speed in millimeters per second, and `b` the permitted blur in pixels. Then:

`blur_pixels ≈ v × effective_exposure_seconds / s`

`effective_exposure_seconds <= b × s / v`

Hypothetical example, not a measurement of this conveyor: at `s = 0.5 mm/pixel`, `v = 1000 mm/s`, and `b = 1 pixel`, the effective exposure must be no more than `0.0005 s = 0.5 ms = 1/2000 s`. Validate the permitted blur against the smallest distinguishing lettering. For flash-dominated capture, pulse duration can determine effective exposure; residual ambient illumination can still create blur, and rolling-shutter timing requires explicit support.

The unknown camera model, sensor/shutter, lens, working distance, field of view, conveyor speed, and trigger interface prevent a defensible final lux or exposure specification. Set brightness at the selected motion-safe exposure so identifying regions have good signal without clipped highlights. Record measured illumination at the bag plane along with camera settings. Lamp watts and color temperature alone do not describe image quality.

**How to select the winning setup**

First optimize geometry on stationary bags with fixed camera settings. Map brightness across a uniform matte reference at expected bag heights, recording minimum/mean illumination and coefficient of variation. This separates lighting variation from differences in bag printing. Inspect text contrast, glare, color shifts, and depth of field on actual folded bags.

Then test moving bags. Hold exposure and gain fixed when comparing geometry or intensity; hold geometry fixed when testing exposure. Include the most similar SKU pairs, dark printed regions, folded bags, glossy variants if present, and realistic dust. Compare both a fixed recognizer across lighting conditions and, separately, models adapted to candidate capture conditions. Otherwise a setup may look worse merely because the model was trained only on the old lighting.

The decisive metrics are SKU top-1 accuracy, confidence/rejection coverage, per-SKU confusion, identifying-text accuracy, clipped-pixel fraction in identifying regions, and latency. Test across production sessions and ambient-light conditions using independent physical bags. Include artwork-only held-out-SKU enrollment so a lighting choice does not help familiar SKUs while increasing the gap to new artwork.

The current sample archive supplies captured images, not controlled lighting comparisons. It cannot establish which proposed arrangement is best; new captures under recorded conditions are required. Read Wu and Gao for contrast/angle design, Zhang et al. for full rectangular-panel coverage, and Singh and Desai for selecting lighting with downstream task results.
