"""Build app-WAV-1.svg and app-WAV-2.svg with full academic detail."""
import base64
import os

def b64_png(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

base = 'paper/figures/appendix_formulas'
imgs = {}
for name in ['wav_fft', 'wav_welch', 'wav_morlet_cwt', 'wav_morlet_wavelet', 'wav_np_decomp']:
    imgs[name] = b64_png(f'{base}/{name}.png')

# ─────────────────────────────────────────────────────────────
# Helper: SVG code block renderer
# ─────────────────────────────────────────────────────────────

def code_box_svg(x, y, w, h, code_str, title="Python"):
    lines = code_str.strip().split('\n')
    out = []
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#1e1e2e" rx="6"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="26" fill="#2a2a40" rx="6"/>')
    out.append(f'<text x="{x+12}" y="{y+18}" font-size="11.5" fill="#aaaacc" font-family="monospace">{title}</text>')
    line_h = (h - 36) / max(len(lines), 1)
    for i, line in enumerate(lines):
        yl = int(y + 38 + i * line_h)
        if line.strip().startswith('#'):
            color = '#6a9955'
        elif line.strip().startswith(('from ', 'import ')):
            color = '#c792ea'
        elif '=' in line and not line.strip().startswith('#'):
            color = '#cdd6f4'
        else:
            color = '#cdd6f4'
        esc = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        out.append(f'<text x="{x+10}" y="{yl}" font-size="11" fill="{color}" font-family="monospace">{esc}</text>')
    return '\n'.join(out)


# ─────────────────────────────────────────────────────────────
# app-WAV-1.svg  — FFT + Wavelet
# ─────────────────────────────────────────────────────────────

code_wav1 = """from scipy.signal import welch
import pywt

# FFT — Welch's method
freqs, psd = welch(ts, fs=12, nperseg=24,
                   noverlap=12)
# 12개월 = 1 cycle/year
amp_12m = psd[np.argmin(
    np.abs(freqs - 1.0))]

# Wavelet — Morlet CWT
scales = np.arange(1, 64)
coeffs, freqs_w = pywt.cwt(
    ts, scales, 'cmor1.5-1.0',
    sampling_period=1/12)
power = np.abs(coeffs) ** 2"""

svg1_lines = []
svg1_lines.append("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 1920 1080" font-family="Pretendard, -apple-system, sans-serif">
<rect width="1920" height="1080" fill="#FFFFFF"/>

<!-- ====== HEADER ====== -->
<text x="80" y="50" font-size="13" fill="#C0392B" font-weight="600" font-family="monospace">&#xBD80;&#xB85D; App-WAV (1/2)</text>
<text x="80" y="88" font-size="38" font-weight="700" fill="#1a1a1a">FFT&#183;Wavelet &#xD480; &#xAC80;&#xC99D; &#8212; Welch&#39;s PSD &#183; Morlet CWT</text>
<text x="80" y="122" font-size="18" fill="#666666">&#8212; Slide 27&#8211;28&#xC758; &#xD1B5;&#xACC4;&#xC801; &#xC2E0;&#xB8B0;&#xC131; &#xC785;&#xC99D;</text>

<!-- ====== SUMMARY BOX ====== -->
<g transform="translate(80,134)">
  <rect x="0" y="0" width="1760" height="64" fill="#FFFAE0" stroke="#d4ac0d" rx="6"/>
  <text x="20" y="24" font-size="14" fill="#1a1a1a">
    <tspan font-weight="700" fill="#C0392B">&#9658; &#xCE21;&#xC815; &#xBC29;&#xBC95;: </tspan>
    <tspan>Welch 1967 PSD (overlapping windows, white-noise null) &#183; Morlet CWT (cone-of-influence, red noise null, Torrence-Compo 1998)</tspan>
  </text>
  <text x="20" y="50" font-size="13.5" fill="#1a1a1a">
    <tspan font-weight="700" fill="#C0392B">&#9658; &#xD575;&#xC2EC; &#xACB0;&#xACFC;: </tspan>
    <tspan>PSD &#xBD84;&#xAE30;(3m) 4 archetype &#xACF5;&#xD1B5; &#x2248;0.27 &#183; &#xC5F0;&#xC8FC;&#xAE30;(12m) C2 &#xCD9C;&#xC5F0;&#xAE08;&#xD615; 0.332 (&#xCD5C;&#xAC15;) &#183; Wavelet C2/C0 &#xD30C;&#xC6CC; &#xD734;163&#xBC30; &#xACA9;&#xCC28;</tspan>
  </text>
</g>""")

# col-A: FFT formulas (x=80, y=210)
svg1_lines.append("""
<!-- ====== COL-A: FFT formulas ====== -->
<text x="80" y="222" font-size="14.5" font-weight="700" fill="#C0392B">&#9312; &#xC774;&#xC0B0; &#xD478;&#xB9AC;&#xC5D0; &#xBCC0;&#xD658; (DFT)</text>""")
svg1_lines.append(f'<image href="{imgs["wav_fft"]}" x="80" y="230" width="540" height="84"/>')
svg1_lines.append("""
<text x="80" y="330" font-size="14.5" font-weight="700" fill="#C0392B">&#9313; Welch&#39;s PSD (&#xBD84;&#xC0B0; &#xAC10;&#xC18C;)</text>""")
svg1_lines.append(f'<image href="{imgs["wav_welch"]}" x="80" y="338" width="540" height="113"/>')
svg1_lines.append("""
<text x="86" y="472" font-size="12" fill="#555555">&#x2022; K segments &#xD3C9;&#xADE0; &#xD0B5; &#xBD84;&#xC0B0; N&#xBC30; &#xAC10;&#xC18C;</text>
<text x="86" y="491" font-size="12" fill="#555555">&#x2022; nperseg=24, noverlap=12 (50% overlap)</text>
<text x="86" y="510" font-size="12" fill="#555555">&#x2022; white-noise null &#xB300;&#xBE44; 12m&#xB7B7;3m &#xC720;&#xC758;</text>
<text x="86" y="529" font-size="12" fill="#555555">&#x2022; &#xC815;&#xC0C1;&#xC131; &#xAC00;&#xC815; &#x2014; &#xCD94;&#xC138;&#xB294; STL&#xB7B7;NP&#xB85C; &#xBCF4;&#xC644;</text>
<text x="86" y="548" font-size="12" fill="#555555">&#x2022; Gibbs &#xD604;&#xC0C1; &#x2192; Wavelet multi-scale &#xBCF4;&#xC644;</text>""")

# col-B: Wavelet formulas (x=660, y=210)
svg1_lines.append("""
<!-- ====== COL-B: Wavelet formulas ====== -->
<text x="660" y="222" font-size="14.5" font-weight="700" fill="#1a6bb5">&#9314; Morlet CWT (&#xC5F0;&#xC18D; &#xC6E8;&#xC774;&#xBE14;&#xB9BF;)</text>""")
svg1_lines.append(f'<image href="{imgs["wav_morlet_cwt"]}" x="660" y="230" width="578" height="86"/>')
svg1_lines.append("""
<text x="660" y="330" font-size="14.5" font-weight="700" fill="#1a6bb5">&#9315; Morlet Wavelet &#xD568;&#xC218;</text>""")
svg1_lines.append(f'<image href="{imgs["wav_morlet_wavelet"]}" x="660" y="338" width="460" height="114"/>')
svg1_lines.append("""
<text x="666" y="472" font-size="12" fill="#555555">&#x2022; s: scale (&#xC8FC;&#xAE30;), &#x3C4;: &#xC2DC;&#xAC04; &#xC704;&#xCE58;</text>
<text x="666" y="491" font-size="12" fill="#555555">&#x2022; &#x3C8;*: complex conjugate of Morlet wavelet</text>
<text x="666" y="510" font-size="12" fill="#555555">&#x2022; &#x3C9;&#x2080;=6: &#xC2DC;&#xAC04;-&#xC8FC;&#xD30C;&#xC218; &#xCD5C;&#xC801; &#xADE0;&#xD615; (Torrence-Compo &#xD45C;&#xC900;)</text>
<text x="666" y="529" font-size="12" fill="#555555">&#x2022; Cone-of-influence: &#xACBD;&#xACC4; edge effect &#xB9C8;&#xC2A4;&#xD06C;</text>
<text x="666" y="548" font-size="12" fill="#555555">&#x2022; Red noise AR(1) null &#xB300;&#xBE44; &#xC720;&#xC758; &#xAC80;&#xC99D;</text>""")

# col-C: code box (x=1266)
svg1_lines.append("""
<!-- ====== COL-C: code box ====== -->
<text x="1266" y="222" font-size="14.5" font-weight="700" fill="#333333">&#9316; &#xAD6C;&#xD604; &#xCF54;&#xB4DC;</text>""")
svg1_lines.append(code_box_svg(1266, 230, 608, 340, code_wav1, "Python — scipy + pywt"))

# PSD table
svg1_lines.append("""
<!-- ====== PSD TABLE ====== -->
<g transform="translate(80,585)">
  <rect x="0" y="0" width="1760" height="172" fill="#fafafa" stroke="#dddddd" rx="6"/>
  <rect x="0" y="0" width="3" height="172" fill="#C0392B"/>

  <text x="16" y="22" font-size="13.5" font-weight="700" fill="#C0392B">PSD &#xD30C;&#xC6CC; &#xD734; Wavelet &#xC2DC;&#xAC04; &#xAC15;&#xD654; &#x2014; 4 Archetype</text>
  <line x1="16" y1="30" x2="1744" y2="30" stroke="#eeeeee" stroke-width="1"/>

  <!-- header row -->
  <rect x="0" y="32" width="1760" height="20" fill="#f0f0f0"/>
  <text x="16"   y="47" font-size="11.5" fill="#666" font-weight="600">Archetype</text>
  <text x="300"  y="47" font-size="11.5" fill="#666" font-weight="600">PSD 3m (&#xBD84;&#xAE30;)</text>
  <text x="520"  y="47" font-size="11.5" fill="#666" font-weight="600">PSD 6m</text>
  <text x="700"  y="47" font-size="11.5" fill="#666" font-weight="600">PSD 12m (&#xC5F0;&#xC8FC;&#xAE30;)</text>
  <text x="950"  y="47" font-size="11.5" fill="#666" font-weight="600">Wavelet ratio (&#xD734;&#xBC30; &#xAC15;&#xD654;, C0 &#xAE30;&#xC900;)</text>
  <text x="1280" y="47" font-size="11.5" fill="#666" font-weight="600">&#xBD84;&#xB958;</text>

  <!-- C0 -->
  <text x="16"   y="70" font-size="13" fill="#1a1a1a">C0 &#xC778;&#xAC74;&#xBE44;&#xD615;</text>
  <text x="300"  y="70" font-size="13" fill="#1a1a1a">0.272</text>
  <text x="520"  y="70" font-size="13" fill="#777">low</text>
  <text x="700"  y="70" font-size="13" fill="#1a1a1a">0.097</text>
  <text x="950"  y="70" font-size="13" fill="#777">&#xD734;1.00 (&#xAE30;&#xC900;)</text>
  <text x="1280" y="70" font-size="12" fill="#777">&#xBE44;&#xAD50;&#xAD70; (null)</text>

  <!-- C1 -->
  <text x="16"   y="92" font-size="13" fill="#1a6bb5">C1 &#xC790;&#xC0B0;&#xCDE8;&#xB4DD;&#xD615;</text>
  <text x="300"  y="92" font-size="13" fill="#1a1a1a">&#x2248;0.27</text>
  <text x="520"  y="92" font-size="13" fill="#777">mid</text>
  <text x="700"  y="92" font-size="13" fill="#1a6bb5">0.172</text>
  <text x="950"  y="92" font-size="13" fill="#1a6bb5">&#xD734;2.75</text>
  <text x="1280" y="92" font-size="12" fill="#1a6bb5">&#xBD84;&#xC11D; &#xB300;&#xC0C1;</text>

  <!-- C2 highlight -->
  <rect x="0" y="100" width="1760" height="20" fill="#fff5f5"/>
  <text x="16"   y="115" font-size="13" fill="#C0392B" font-weight="700">C2 &#xCD9C;&#xC5F0;&#xAE08;&#xD615;</text>
  <text x="300"  y="115" font-size="13" fill="#1a1a1a">0.163</text>
  <text x="520"  y="115" font-size="13" fill="#777">high</text>
  <text x="700"  y="115" font-size="13" fill="#C0392B" font-weight="700">0.332 &#x2605;</text>
  <text x="950"  y="115" font-size="13" fill="#C0392B" font-weight="700">&#xD734;6.54 &#x2605;</text>
  <text x="1280" y="115" font-size="12" fill="#C0392B" font-weight="600">&#xBD84;&#xC11D; &#xB300;&#xC0C1; (&#xCD5C;&#xAC15;)</text>

  <!-- C3 -->
  <text x="16"   y="137" font-size="13" fill="#2e7d32">C3 &#xC815;&#xC0C1;&#xC0AC;&#xC5C5;</text>
  <text x="300"  y="137" font-size="13" fill="#1a1a1a">&#x2248;0.27</text>
  <text x="520"  y="137" font-size="13" fill="#777">mid</text>
  <text x="700"  y="137" font-size="13" fill="#2e7d32">0.115</text>
  <text x="950"  y="137" font-size="13" fill="#2e7d32">&#xD734;4.17</text>
  <text x="1280" y="137" font-size="12" fill="#2e7d32">&#xBE44;&#xAD50;&#xAD70;</text>

  <text x="16"   y="158" font-size="11" fill="#999">3m &#xBD84;&#xAE30; &#xBC15;&#xC790;&#xB294; 4 archetype &#xACF5;&#xD1B5; (~0.27). 12m &#xC5F0;&#xC8FC;&#xAE30;&#xB294; C2 &#xCD9C;&#xC5F0;&#xAE08;&#xD615;&#xB9CC; &#xC555;&#xB3C4;&#xC801;. Wavelet ratio = 2025 &#xB300; 2015 &#xD3C9;&#xADE0; &#xD30C;&#xC6CC; &#xBE44;&#xC728;.</text>
</g>""")

# Citations
svg1_lines.append("""
<!-- ====== CITATIONS ====== -->
<line x1="80" y1="772" x2="1840" y2="772" stroke="#e0e0e0" stroke-width="1"/>
<text x="80" y="790" font-size="11" fill="#888888">Welch, P. D. (1967). <tspan font-style="italic">The Use of Fast Fourier Transform for the Estimation of Power Spectra.</tspan> IEEE Trans. Audio Electroacoust. 15(2): 70&#x2013;73.</text>
<text x="80" y="808" font-size="11" fill="#888888">Torrence, C., &amp; Compo, G. P. (1998). <tspan font-style="italic">A Practical Guide to Wavelet Analysis.</tspan> Bull. Amer. Meteor. Soc. 79(1): 61&#x2013;78.</text>

<!-- ====== BOTTOM LINE ====== -->
<text x="960" y="858" text-anchor="middle" font-size="22" font-weight="700" fill="#1a1a1a">&#xCD9C;&#xC5F0;&#xAE08;&#xD615;&#xC758; &#xBC15;&#xC790;&#xB294; &#xC2DC;&#xAC04;&#xC774; &#xAC08;&#xC218;&#xB85D; &#xAC15;&#xD574;&#xC9C4;&#xB2E4; &#8212; &#xD55C; &#xC8FC;&#xD30C;&#xC218; &#xC6B0;&#xC5F0; &#xC544;&#xB2C8;&#xB2E4;.</text>

<!-- ====== PAGE INDICATOR ====== -->
<text x="80" y="1056" font-size="13" font-family="monospace" fill="#666666">App-WAV 1 / 2</text>
<text x="1840" y="1056" text-anchor="end" font-size="12" fill="#666666" font-style="italic">NP &#xBD84;&#xD574;&#xB7B7;AR-Net robustness&#xB7B7;&#xD2B8;&#xB77C;&#xC774;&#xC559;&#xAD6C;&#xB808;&#xC774;&#xC158; &#x2192; App-WAV (2/2)</text>

</svg>""")

svg1_content = '\n'.join(svg1_lines)
with open('paper/재정데이터 분석 ppt/wireframes/app-WAV-1.svg', 'w', encoding='utf-8') as f:
    f.write(svg1_content)
print(f'app-WAV-1.svg written: {len(svg1_content)//1024} KB')


# ─────────────────────────────────────────────────────────────
# app-WAV-2.svg  — NeuralProphet + AR-Net robustness + Triangulation
# ─────────────────────────────────────────────────────────────

code_wav2 = """from neuralprophet import NeuralProphet
m = NeuralProphet(
    yearly_seasonality=True,
    n_changepoints=10,
    n_lags=12, n_forecasts=12,
    ar_layers=[],
    quantiles=[0.05, 0.95],
    epochs=300)
metrics = m.fit(df, freq='MS',
                progress='none')
future = m.make_future_dataframe(
    df, periods=12,
    n_historic_predictions=True)
forecast = m.predict(future)
# AR-Net robustness:
# n_lags=0 vs n_lags=12 비교"""

svg2_lines = []
svg2_lines.append("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 1920 1080" font-family="Pretendard, -apple-system, sans-serif">
<rect width="1920" height="1080" fill="#FFFFFF"/>

<!-- ====== HEADER ====== -->
<text x="80" y="50" font-size="13" fill="#C0392B" font-weight="600" font-family="monospace">&#xBD80;&#xB85D; App-WAV (2/2)</text>
<text x="80" y="88" font-size="38" font-weight="700" fill="#1a1a1a">NeuralProphet &#xBD84;&#xD574; &#183; AR-Net Robustness &#183; &#xD2B8;&#xB77C;&#xC774;&#xC559;&#xAD6C;&#xB808;&#xC774;&#xC158;</text>
<text x="80" y="122" font-size="18" fill="#666666">&#8212; Slide 29&#x2013;30&#xC758; &#xD1B5;&#xACC4;&#xC801; &#xC2E0;&#xB8B0;&#xC131; &#xC785;&#xC99D;</text>

<!-- ====== SUMMARY BOX ====== -->
<g transform="translate(80,134)">
  <rect x="0" y="0" width="1760" height="64" fill="#FFFAE0" stroke="#d4ac0d" rx="6"/>
  <text x="20" y="24" font-size="14" fill="#1a1a1a">
    <tspan font-weight="700" fill="#C0392B">&#9658; &#xCE21;&#xC815; &#xBC29;&#xBC95;: </tspan>
    <tspan>NP &#xBD84;&#xD574; (trend + seasonality, Triebe 2021) &#183; AR-Net &#xD3EC;&#xD568;/&#xC81C;&#xC678; spec &#xBE44;&#xAD50; (n_lags=0 vs 12) &#183; 14&#xBD84;&#xC57C; &#xD73C;3 &#xB3C4;&#xAD6C; outcome &#xC0C1;&#xAD00;</tspan>
  </text>
  <text x="20" y="50" font-size="13.5" fill="#1a1a1a">
    <tspan font-weight="700" fill="#C0392B">&#9658; &#xD575;&#xC2EC; &#xACB0;&#xACFC;: </tspan>
    <tspan>C2 seasonality strength 0.458 (&#xCD5C;&#xAC15;) &#183; AR-Net &#xD3EC;&#xD568; &#xC2DC; |&#x394;|&lt;0.03 (robust) &#183; &#xBCF4;&#xAC74;&#xB7B7;&#xD1B5;&#xC2E0;&#xB7B7;&#xACF5;&#xACF5;&#xC9C8;&#xC11C;&#xB7B7;&#xAD50;&#xC721; &#xC138; &#xB3C4;&#xAD6C; &#xBAA8;&#xB450; &#xC74C;</tspan>
  </text>
</g>""")

# col-A: NP formula + code (x=80)
svg2_lines.append("""
<!-- ====== COL-A: NP formula + code ====== -->
<text x="80" y="220" font-size="14.5" font-weight="700" fill="#C0392B">&#9312; NeuralProphet &#xBD84;&#xD574; &#xBAA8;&#xD615;</text>""")
svg2_lines.append(f'<image href="{imgs["wav_np_decomp"]}" x="80" y="228" width="580" height="144"/>')
svg2_lines.append("""
<text x="86" y="390" font-size="12" fill="#555555">&#x2022; T(t): piecewise linear &#xCD94;&#xC138;, changepoint &#xC790;&#xB3D9; &#xAC10;&#xC9C0;</text>
<text x="86" y="408" font-size="12" fill="#555555">&#x2022; S(t): Fourier &#xACC4;&#xC808;&#xC131; (yearly_seasonality=True)</text>
<text x="86" y="426" font-size="12" fill="#555555">&#x2022; AR(t): AR-Net &#xC790;&#xAE30;&#xC0C1;&#xAD00; (n_lags=12 &#xC2DC; &#xD65C;&#xC131;&#xD654;)</text>
<text x="86" y="444" font-size="12" fill="#555555">&#x2022; &#xC78C;&#xB9AC;&#xC9C0; &#xBAA9;&#xD45C;: &#xCD94;&#xC138; &#xC81C;&#xAC70; &#xD6C4; &#xC794;&#xC874; &#xACC4;&#xC808;&#xC131; &#xAC80;&#xC99D;</text>

<!-- code box -->
<text x="80" y="468" font-size="14.5" font-weight="700" fill="#333333">&#9313; &#xAD6C;&#xD604; &#xCF54;&#xB4DC;</text>""")
svg2_lines.append(code_box_svg(80, 476, 580, 320, code_wav2, "Python — neuralprophet"))

# col-B: AR-Net robustness table (x=700)
svg2_lines.append("""
<!-- ====== COL-B: AR-Net table ====== -->
<text x="700" y="220" font-size="14.5" font-weight="700" fill="#1a6bb5">&#9314; AR-Net Robustness &#xAC80;&#xC99D; (n_lags=0 vs 12)</text>
<g transform="translate(700, 230)">
  <rect x="0" y="0" width="560" height="190" fill="#fafafa" stroke="#dddddd" rx="5"/>

  <!-- header -->
  <rect x="0" y="0" width="560" height="22" fill="#e8eaf6" rx="5"/>
  <text x="10"  y="16" font-size="11.5" fill="#444" font-weight="600">Archetype</text>
  <text x="150" y="16" font-size="11.5" fill="#444" font-weight="600">Spec A (n_lags=0)</text>
  <text x="290" y="16" font-size="11.5" fill="#444" font-weight="600">Spec B (n_lags=12)</text>
  <text x="400" y="16" font-size="11.5" fill="#444" font-weight="600">&#x394;</text>
  <text x="440" y="16" font-size="11.5" fill="#444" font-weight="600">ACF p-val</text>

  <!-- C0 -->
  <text x="10"  y="40" font-size="12.5" fill="#1a1a1a">C0 &#xC778;&#xAC74;&#xBE44;&#xD615;</text>
  <text x="150" y="40" font-size="12.5" fill="#1a1a1a">0.274</text>
  <text x="290" y="40" font-size="12.5" fill="#1a1a1a">0.246</text>
  <text x="400" y="40" font-size="12.5" fill="#555">&#x2212;0.028</text>
  <text x="440" y="40" font-size="12.5" fill="#555">~0.4</text>

  <!-- C1 -->
  <text x="10"  y="62" font-size="12.5" fill="#1a6bb5">C1 &#xC790;&#xC0B0;&#xCDE8;&#xB4DD;</text>
  <text x="150" y="62" font-size="12.5" fill="#1a6bb5">0.281</text>
  <text x="290" y="62" font-size="12.5" fill="#1a6bb5">0.280</text>
  <text x="400" y="62" font-size="12.5" fill="#1a6bb5">&#x2212;0.002</text>
  <text x="440" y="62" font-size="12.5" fill="#555">~0.5</text>

  <!-- C2 highlight -->
  <rect x="0" y="69" width="560" height="20" fill="#fff5f5"/>
  <text x="10"  y="84" font-size="12.5" fill="#C0392B" font-weight="700">C2 &#xCD9C;&#xC5F0;&#xAE08;&#xD615;</text>
  <text x="150" y="84" font-size="12.5" fill="#C0392B" font-weight="700">0.458</text>
  <text x="290" y="84" font-size="12.5" fill="#C0392B">0.431</text>
  <text x="400" y="84" font-size="12.5" fill="#C0392B">&#x2212;0.027</text>
  <text x="440" y="84" font-size="12.5" fill="#555">~0.3</text>

  <!-- C3 -->
  <text x="10"  y="106" font-size="12.5" fill="#2e7d32">C3 &#xC815;&#xC0C1;&#xC0AC;&#xC5C5;</text>
  <text x="150" y="106" font-size="12.5" fill="#2e7d32">0.390</text>
  <text x="290" y="106" font-size="12.5" fill="#2e7d32">0.405</text>
  <text x="400" y="106" font-size="12.5" fill="#2e7d32">+0.015</text>
  <text x="440" y="106" font-size="12.5" fill="#555">~0.4</text>

  <!-- divider -->
  <line x1="0" y1="113" x2="560" y2="113" stroke="#ddd" stroke-width="1"/>
  <!-- conclusion row -->
  <rect x="0" y="113" width="560" height="20" fill="#e8f5e9" rx="0"/>
  <text x="10"  y="128" font-size="12" fill="#2e7d32" font-weight="700">&#xACB0;&#xB860;</text>
  <text x="150" y="128" font-size="12" fill="#555" font-style="italic">seasonality</text>
  <text x="290" y="128" font-size="12" fill="#555" font-style="italic">seasonality</text>
  <text x="400" y="128" font-size="12" fill="#2e7d32" font-weight="700">|&#x394;|&lt;0.03</text>
  <text x="440" y="128" font-size="12" fill="#2e7d32">robust</text>

  <text x="10"  y="152" font-size="11" fill="#777">AR-Net &#xC640;&#xC774;&#xAC00; &#xD3EC;&#xD568;&#xB418;&#xC5B4;&#xB3C4; &#xACC4;&#xC808;&#xC131; &#xCD94;&#xC815;&#xAC12; &#xBCC0;&#xD654; |&#x394;| &lt;0.03 &#x2014; &#xBD84;&#xC11D; &#xACB0;&#xACFC; spec &#xB3C5;&#xB9BD;&#xC801;.</text>
  <text x="10"  y="170" font-size="11" fill="#777">&#xC794;&#xCC28; ACF p-value ~0.3&#x2013;0.5 (&#xC2DC;&#xACC4;&#xC5F4; &#xAD6C;&#xC870; &#xC794;&#xC874; &#xC5C6;&#xC74C;).</text>
</g>

<!-- triangulation summary -->
<text x="700" y="444" font-size="14.5" font-weight="700" fill="#6a0dad">&#9315; &#xD2B8;&#xB77C;&#xC774;&#xC559;&#xAD6C;&#xB808;&#xC774;&#xC158; &#x2014; 3 &#xB3C4;&#xAD6C; &#xBC1C;&#xC0B0;</text>
<g transform="translate(700, 454)">
  <rect x="0" y="0" width="560" height="148" fill="#f8f4ff" stroke="#b39ddb" rx="5"/>

  <!-- header -->
  <rect x="0" y="0" width="560" height="20" fill="#ede7f6" rx="5"/>
  <text x="10" y="15" font-size="11.5" fill="#444" font-weight="600">&#xB3C4;&#xAD6C;</text>
  <text x="100" y="15" font-size="11.5" fill="#444" font-weight="600">&#xCE21;&#xB3C4;</text>
  <text x="270" y="15" font-size="11.5" fill="#444" font-weight="600">&#xC0AC;&#xD68C;&#xBCF5;&#xC9C0; r</text>
  <text x="360" y="15" font-size="11.5" fill="#444" font-weight="600">&#xBE44;&#xACE0;</text>

  <text x="10"  y="38" font-size="12.5" fill="#C0392B" font-weight="600">FFT</text>
  <text x="100" y="38" font-size="12" fill="#555">amp_12m_norm</text>
  <text x="270" y="38" font-size="12.5" fill="#C0392B" font-weight="700">&#x2212;0.86 &#x2605;</text>
  <text x="360" y="38" font-size="11.5" fill="#555">&#xAC00;&#xC7A5; &#xAC15;&#xD55C; &#xC2E0;&#xD638;</text>

  <text x="10"  y="60" font-size="12.5" fill="#888">STL</text>
  <text x="100" y="60" font-size="12" fill="#555">seasonal_strength</text>
  <text x="270" y="60" font-size="12.5" fill="#888">+0.003</text>
  <text x="360" y="60" font-size="11.5" fill="#888">signal vanish &#x2014; &#xCD94;&#xC138; &#xD761;&#xC218;</text>

  <text x="10"  y="82" font-size="12.5" fill="#1a6bb5" font-weight="600">NeuralProphet</text>
  <text x="100" y="82" font-size="12" fill="#555">yearly_seasonality</text>
  <text x="270" y="82" font-size="12.5" fill="#1a6bb5" font-weight="700">&#x2212;0.24</text>
  <text x="360" y="82" font-size="11.5" fill="#555">changepoint&#xC73C;&#xB85C; &#xBD80;&#xBD84; &#xBCF5;&#xC6D0;</text>

  <line x1="0" y1="90" x2="560" y2="90" stroke="#ddd" stroke-width="1"/>
  <text x="10" y="106" font-size="11.5" fill="#555">&#x2022; STL &#xC2E0;&#xD638; &#xC18C;&#xBA78;: &#xAC8C;&#xC784;&#xD654; &#xC810;&#xD504;&#xB97C; &#xCD94;&#xC138;&#xB85C; &#xD765;&#xC218;. FFT vs NP&#xAC00; &#xCD94;&#xC138; &#xC81C;&#xAC70; &#xD6C4; &#xACC4;&#xC808;&#xC131; &#xC720;&#xC9C0;&#xB97C; &#xC9C0;&#xC9C0;.</text>
  <text x="10" y="124" font-size="11.5" fill="#555">&#x2022; &#xBC1C;&#xC0B0;&#xC740; &#xC790;&#xAE30; &#xBE44;&#xD310;&#xC758; &#xCD9C;&#xBC1C;&#xC810;. &#xD569;&#xC758;&#xAC00; &#xC544;&#xB2CC; &#xC0C1;&#xD638; &#xBCF4;&#xC644; &#xD655;&#xC778;.</text>
  <text x="10" y="142" font-size="11" fill="#888">&#xB3C4;&#xAD6C; &#xAC04; raw r: FFT-STL &#x2212;0.13, FFT-NP &#x2212;0.07, STL-NP &#x2212;0.02 (&#xC11C;&#xB85C; &#xB2E4;&#xB978; &#xCE21;&#xBA74; &#xCE21;&#xC815; &#x2192; &#xC0C1;&#xD638; &#xBCF4;&#xC644; &#xAC80;&#xC99D;)</text>
</g>""")

# col-C (right side) x=1300 — chart placeholders (smaller now) + note
svg2_lines.append("""
<!-- ====== COL-C: chart placeholders + note ====== -->
<text x="1300" y="220" font-size="14.5" font-weight="700" fill="#333333">&#9316; &#xCC38;&#xC870; &#xCC28;&#xD2B8;</text>
<rect x="1300" y="230" width="558" height="230" fill="#f8f8f8" stroke="#cccccc" stroke-width="1.5" stroke-dasharray="8,4" rx="6"/>
<text x="1579" y="338" text-anchor="middle" font-size="14" fill="#999" font-style="italic">[ NP &#xBD84;&#xD574; ]</text>
<text x="1579" y="362" text-anchor="middle" font-size="12" fill="#999" font-family="monospace">h29_np_decomposition.png</text>

<rect x="1300" y="472" width="558" height="230" fill="#f8f8f8" stroke="#cccccc" stroke-width="1.5" stroke-dasharray="8,4" rx="6"/>
<text x="1579" y="580" text-anchor="middle" font-size="14" fill="#999" font-style="italic">[ AR-Net Robustness ]</text>
<text x="1579" y="604" text-anchor="middle" font-size="12" fill="#999" font-family="monospace">h29_np_arnet_robustness.png</text>""")

# KPI bottom bar
svg2_lines.append("""
<!-- ====== KPI BAR ====== -->
<g transform="translate(80,812)">
  <rect x="0" y="0" width="1760" height="96" fill="#fafafa" stroke="#dddddd" rx="6"/>
  <rect x="0" y="0" width="3" height="96" fill="#C0392B"/>
  <text x="16" y="22" font-size="13.5" font-weight="700" fill="#C0392B">KPI &#x2014; seasonality strength &#183; AR-Net &#x394; &#183; 14&#xBD84;&#xC57C; &#xBD80;&#xD638; &#xC77C;&#xCE58; &#183; &#xB3C4;&#xAD6C; &#xAC04; raw r</text>
  <line x1="16" y1="30" x2="1744" y2="30" stroke="#eeeeee" stroke-width="1"/>

  <text x="16"   y="50" font-size="11.5" fill="#888" font-weight="600">Seasonality Strength</text>
  <text x="440"  y="50" font-size="11.5" fill="#888" font-weight="600">AR-Net |&#x394;|</text>
  <text x="740"  y="50" font-size="11.5" fill="#888" font-weight="600">14&#xBD84;&#xC57C; &#xBD80;&#xD638; &#xC77C;&#xCE58;</text>
  <text x="1120" y="50" font-size="11.5" fill="#888" font-weight="600">&#xB3C4;&#xAD6C; &#xAC04; raw r</text>

  <text x="16"   y="70" font-size="13" fill="#1a1a1a">C2 <tspan font-weight="700" fill="#C0392B">0.458 &#x2605;</tspan>  C3 0.390  C1 0.281  C0 0.274</text>
  <text x="440"  y="70" font-size="13" fill="#1a1a1a">&#xD3EC;&#xD568; vs &#xC81C;&#xC678; <tspan font-weight="700" fill="#2e7d32">&lt;0.03</tspan> (&#xBAA8;&#xB4E0; archetype robust)</text>
  <text x="740"  y="70" font-size="13" fill="#1a1a1a">&#xBCF4;&#xAC74;&#xB7B7;&#xD1B5;&#xC2E0;&#xB7B7;&#xACF5;&#xACF5;&#xC9C8;&#xC11C;&#xB7B7;&#xAD50;&#xC721; &#xC138; &#xB3C4;&#xAD6C; &#xBAA8;&#xB450; &#xC74C;</text>
  <text x="1120" y="70" font-size="13" fill="#1a1a1a">FFT&#x2013;STL: <tspan fill="#555" font-weight="600">&#x2212;0.13</tspan>  FFT&#x2013;NP: <tspan fill="#555" font-weight="600">&#x2212;0.07</tspan>  STL&#x2013;NP: <tspan fill="#555" font-weight="600">&#x2212;0.02</tspan></text>

  <text x="16" y="88" font-size="11" fill="#999">&#xCC38;&#xACE0;&#xBB38;&#xD5CC;: Triebe et al. (2021) NeuralProphet arXiv:2111.15397</text>
</g>

<!-- ====== BOTTOM LINE ====== -->
<text x="960" y="946" text-anchor="middle" font-size="22" font-weight="700" fill="#1a1a1a">&#xC138; &#xB3C4;&#xAD6C;&#xAC00; &#xB2E4;&#xB978; &#xCE21;&#xBA74;&#xC744; &#xBCF4;&#xC9C0;&#xB9CC; &#xAC19;&#xC740; &#xBC29;&#xD5A5;&#xC744; &#xAC00;&#xB9AC;&#xD0A8;&#xB2E4; &#8212; &#xC0C1;&#xD638; &#xBCF4;&#xC644;&#xC774; &#xAC80;&#xC99D;&#xC774;&#xB2E4;.</text>

<!-- ====== CITATIONS ====== -->
<text x="80" y="978" font-size="11" fill="#888888">Triebe, O., Hewamalage, H., Pilyugina, P., Laptev, N., Bergmeir, C., &amp; Rajagopal, R. (2021). <tspan font-style="italic">NeuralProphet: Explainable Forecasting at Scale.</tspan> arXiv:2111.15397.</text>
<text x="80" y="996" font-size="11" fill="#888888">Welch (1967) &#xB7B7; Torrence &amp; Compo (1998) &#x2192; App-WAV (1/2) &#xCC38;&#xC870;.</text>

<!-- ====== PAGE INDICATOR ====== -->
<text x="80" y="1056" font-size="13" font-family="monospace" fill="#666666">App-WAV 2 / 2</text>
<text x="1840" y="1056" text-anchor="end" font-size="12" fill="#666666" font-style="italic">FFT&#xB7B7;Wavelet &#xD480; &#xAC80;&#xC99D; &#x2190; App-WAV (1/2)</text>

</svg>""")

svg2_content = '\n'.join(svg2_lines)
with open('paper/재정데이터 분석 ppt/wireframes/app-WAV-2.svg', 'w', encoding='utf-8') as f:
    f.write(svg2_content)
print(f'app-WAV-2.svg written: {len(svg2_content)//1024} KB')

print('Done.')
