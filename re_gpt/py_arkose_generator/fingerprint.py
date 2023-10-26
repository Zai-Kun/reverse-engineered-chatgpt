import base64
import os
import random
import re

from .murmur import x64hash128

baseFingerprint = {
    "DNT": "unknown",
    "L": "en-US",
    "D": 24,
    "PR": 1,
    "S": [1920, 1200],
    "AS": [1920, 1200],
    "TO": 9999,
    "SS": True,
    "LS": True,
    "IDB": True,
    "B": False,
    "ODB": True,
    "CPUC": "unknown",
    "PK": "Win32",
    "CFP": f"canvas winding:yes~canvas fp:data:image/png;base64,{base64.b64encode(str(random.random()).encode()).decode()}",
    "FR": False,
    "FOS": False,
    "FB": False,
    "JSF": [
        "Andale Mono",
        "Arial",
        "Arial Black",
        "Arial Hebrew",
        "Arial MT",
        "Arial Narrow",
        "Arial Rounded MT Bold",
        "Arial Unicode MS",
        "Bitstream Vera Sans Mono",
        "Book Antiqua",
        "Bookman Old Style",
        "Calibri",
        "Cambria",
        "Cambria Math",
        "Century",
        "Century Gothic",
        "Century Schoolbook",
        "Comic Sans",
        "Comic Sans MS",
        "Consolas",
        "Courier",
        "Courier New",
        "Garamond",
        "Geneva",
        "Georgia",
        "Helvetica",
        "Helvetica Neue",
        "Impact",
        "Lucida Bright",
        "Lucida Calligraphy",
        "Lucida Console",
        "Lucida Fax",
        "LUCIDA GRANDE",
        "Lucida Handwriting",
        "Lucida Sans",
        "Lucida Sans Typewriter",
        "Lucida Sans Unicode",
        "Microsoft Sans Serif",
        "Monaco",
        "Monotype Corsiva",
        "MS Gothic",
        "MS Outlook",
        "MS PGothic",
        "MS Reference Sans Serif",
        "MS Sans Serif",
        "MS Serif",
        "MYRIAD",
        "MYRIAD PRO",
        "Palatino",
        "Palatino Linotype",
        "Segoe Print",
        "Segoe Script",
        "Segoe UI",
        "Segoe UI Light",
        "Segoe UI Semibold",
        "Segoe UI Symbol",
        "Tahoma",
        "Times",
        "Times New Roman",
        "Times New Roman PS",
        "Trebuchet MS",
        "Verdana",
        "Wingdings",
        "Wingdings 2",
        "Wingdings 3",
    ],
    "P": [
        "Chrome PDF Plugin::Portable Document Format::application/x-google-chrome-pdf~pdf",
        "Chrome PDF Viewer::::application/pdf~pdf",
        "Native Client::::application/x-nacl~,application/x-pnacl~",
    ],
    "T": [0, False, False],
    "H": 24,
    "SWF": False,  # Flash support
}

languages = [
    "af",
    "af-ZA",
    "ar",
    "ar-AE",
    "ar-BH",
    "ar-DZ",
    "ar-EG",
    "ar-IQ",
    "ar-JO",
    "ar-KW",
    "ar-LB",
    "ar-LY",
    "ar-MA",
    "ar-OM",
    "ar-QA",
    "ar-SA",
    "ar-SY",
    "ar-TN",
    "ar-YE",
    "az",
    "az-AZ",
    "az-AZ",
    "be",
    "be-BY",
    "bg",
    "bg-BG",
    "bs-BA",
    "ca",
    "ca-ES",
    "cs",
    "cs-CZ",
    "cy",
    "cy-GB",
    "da",
    "da-DK",
    "de",
    "de-AT",
    "de-CH",
    "de-DE",
    "de-LI",
    "de-LU",
    "dv",
    "dv-MV",
    "el",
    "el-GR",
    "en",
    "en-AU",
    "en-BZ",
    "en-CA",
    "en-CB",
    "en-GB",
    "en-IE",
    "en-JM",
    "en-NZ",
    "en-PH",
    "en-TT",
    "en-US",
    "en-ZA",
    "en-ZW",
    "eo",
    "es",
    "es-AR",
    "es-BO",
    "es-CL",
    "es-CO",
    "es-CR",
    "es-DO",
    "es-EC",
    "es-ES",
    "es-ES",
    "es-GT",
    "es-HN",
    "es-MX",
    "es-NI",
    "es-PA",
    "es-PE",
    "es-PR",
    "es-PY",
    "es-SV",
    "es-UY",
    "es-VE",
    "et",
    "et-EE",
    "eu",
    "eu-ES",
    "fa",
    "fa-IR",
    "fi",
    "fi-FI",
    "fo",
    "fo-FO",
    "fr",
    "fr-BE",
    "fr-CA",
    "fr-CH",
    "fr-FR",
    "fr-LU",
    "fr-MC",
    "gl",
    "gl-ES",
    "gu",
    "gu-IN",
    "he",
    "he-IL",
    "hi",
    "hi-IN",
    "hr",
    "hr-BA",
    "hr-HR",
    "hu",
    "hu-HU",
    "hy",
    "hy-AM",
    "id",
    "id-ID",
    "is",
    "is-IS",
    "it",
    "it-CH",
    "it-IT",
    "ja",
    "ja-JP",
    "ka",
    "ka-GE",
    "kk",
    "kk-KZ",
    "kn",
    "kn-IN",
    "ko",
    "ko-KR",
    "kok",
    "kok-IN",
    "ky",
    "ky-KG",
    "lt",
    "lt-LT",
    "lv",
    "lv-LV",
    "mi",
    "mi-NZ",
    "mk",
    "mk-MK",
    "mn",
    "mn-MN",
    "mr",
    "mr-IN",
    "ms",
    "ms-BN",
    "ms-MY",
    "mt",
    "mt-MT",
    "nb",
    "nb-NO",
    "nl",
    "nl-BE",
    "nl-NL",
    "nn-NO",
    "ns",
    "ns-ZA",
    "pa",
    "pa-IN",
    "pl",
    "pl-PL",
    "ps",
    "ps-AR",
    "pt",
    "pt-BR",
    "pt-PT",
    "qu",
    "qu-BO",
    "qu-EC",
    "qu-PE",
    "ro",
    "ro-RO",
    "ru",
    "ru-RU",
    "sa",
    "sa-IN",
    "se",
    "se-FI",
    "se-FI",
    "se-FI",
    "se-NO",
    "se-NO",
    "se-NO",
    "se-SE",
    "se-SE",
    "se-SE",
    "sk",
    "sk-SK",
    "sl",
    "sl-SI",
    "sq",
    "sq-AL",
    "sr-BA",
    "sr-BA",
    "sr-SP",
    "sr-SP",
    "sv",
    "sv-FI",
    "sv-SE",
    "sw",
    "sw-KE",
    "syr",
    "syr-SY",
    "ta",
    "ta-IN",
    "te",
    "te-IN",
    "th",
    "th-TH",
    "tl",
    "tl-PH",
    "tn",
    "tn-ZA",
    "tr",
    "tr-TR",
    "tt",
    "tt-RU",
    "ts",
    "uk",
    "uk-UA",
    "ur",
    "ur-PK",
    "uz",
    "uz-UZ",
    "uz-UZ",
    "vi",
    "vi-VN",
    "xh",
    "xh-ZA",
    "zh",
    "zh-CN",
    "zh-HK",
    "zh-MO",
    "zh-SG",
    "zh-TW",
    "zu",
    "zu-ZA",
]

screenRes = [
    [1920, 1080],
    [1920, 1200],
    [2048, 1080],
    [2560, 1440],
    [1366, 768],
    [1440, 900],
    [1536, 864],
    [1680, 1050],
    [1280, 1024],
    [1280, 800],
    [1280, 720],
    [1600, 1200],
    [1600, 900],
]


def randomScreenRes():
    return random.choice(screenRes)


def getFingerprint():
    fingerprint = baseFingerprint.copy()  # Create a copy of the base fingerprint

    fingerprint["DNT"] = "unknown"
    fingerprint["L"] = random.choice(languages)
    fingerprint["D"] = random.choice([8, 24])
    fingerprint["PR"] = round(random.uniform(0, 1) * 2 + 0.5, 2)
    fingerprint["S"] = randomScreenRes()
    fingerprint["AS"] = fingerprint["S"]
    fingerprint["TO"] = (random.randint(-12, 11)) * 60
    fingerprint["SS"] = random.random() > 0.5
    fingerprint["LS"] = random.random() > 0.5
    fingerprint["IDB"] = random.random() > 0.5
    fingerprint["B"] = random.random() > 0.5
    fingerprint["ODB"] = random.random() > 0.5
    fingerprint["CPUC"] = "unknown"
    fingerprint["PK"] = "Win32"
    random_data = base64.b64encode(os.urandom(128)).decode("utf-8")
    fingerprint["CFP"] = (
        "canvas winding:yes~canvas fp:data:image/png;base64," + random_data
    )
    fingerprint["FR"] = False  # Fake Resolution
    fingerprint["FOS"] = False  # Fake Operating System
    fingerprint["FB"] = False  # Fake Browser
    fingerprint["JSF"] = [item for item in fingerprint["JSF"] if random.random() > 0.5]
    fingerprint["P"] = [item for item in fingerprint["P"] if random.random() > 0.5]
    fingerprint["T"] = [
        random.randint(0, 7),
        random.random() > 0.5,
        random.random() > 0.5,
    ]
    fingerprint["H"] = 2 ** random.randint(0, 5)
    fingerprint["SWF"] = fingerprint["SWF"]  # RIP Flash

    return fingerprint


def prepareF(fingerprint):
    f = []
    for key in fingerprint:
        if isinstance(fingerprint[key], list):
            f.append(";".join(map(str, fingerprint[key])))
        else:
            f.append(str(fingerprint[key]))
    return "~~~".join(f)


def cfpHash(H8W):
    l8W, U8W = 0, 0
    if not H8W:
        return ""

    if hasattr(list, "reduce"):
        return str(
            reduce(lambda p8W, z8W: (p8W << 5) - p8W + ord(z8W), H8W, 0) & 0xFFFFFFFF
        )

    for k8W in range(len(H8W)):
        U8W = ord(H8W[k8W])
        l8W = (l8W << 5) - l8W + U8W
        l8W = l8W & l8W

    return str(l8W & 0xFFFFFFFF)


def prepareFe(fingerprint):
    fe = []
    for key in fingerprint:
        if key == "CFP":
            fe.append(f"{key}:{cfpHash(fingerprint[key])}")
        elif key == "P":
            fe.append(f"{key}:{[v.split('::')[0] for v in fingerprint[key]]}")
        else:
            fe.append(f"{key}:{fingerprint[key]}")
    return fe


baseEnhancedFingerprint = {
    "webgl_extensions": "ANGLE_instanced_arrays;EXT_blend_minmax;EXT_color_buffer_half_float;EXT_disjoint_timer_query;EXT_float_blend;EXT_frag_depth;EXT_shader_texture_lod;EXT_texture_compression_bptc;EXT_texture_compression_rgtc;EXT_texture_filter_anisotropic;EXT_sRGB;KHR_parallel_shader_compile;OES_element_index_uint;OES_fbo_render_mipmap;OES_standard_derivatives;OES_texture_float;OES_texture_float_linear;OES_texture_half_float;OES_texture_half_float_linear;OES_vertex_array_object;WEBGL_color_buffer_float;WEBGL_compressed_texture_s3tc;WEBGL_compressed_texture_s3tc_srgb;WEBGL_debug_renderer_info;WEBGL_debug_shaders;WEBGL_depth_texture;WEBGL_draw_buffers;WEBGL_lose_context;WEBGL_multi_draw",
    "webgl_extensions_hash": "58a5a04a5bef1a78fa88d5c5098bd237",
    "webgl_renderer": "WebKit WebGL",
    "webgl_vendor": "WebKit",
    "webgl_version": "WebGL 1.0 (OpenGL ES 2.0 Chromium)",
    "webgl_shading_language_version": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
    "webgl_aliased_line_width_range": "[1, 1]",
    "webgl_aliased_point_size_range": "[1, 1023]",
    "webgl_antialiasing": "yes",
    "webgl_bits": "8,8,24,8,8,0",
    "webgl_max_params": "16,64,16384,4096,8192,32,8192,31,16,32,4096",
    "webgl_max_viewport_dims": "[8192, 8192]",
    "webgl_unmasked_vendor": "Google Inc. (Google)",
    "webgl_unmasked_renderer": "ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)",
    "webgl_vsf_params": "23,127,127,23,127,127,23,127,127",
    "webgl_vsi_params": "0,31,30,0,31,30,0,31,30",
    "webgl_fsf_params": "23,127,127,23,127,127,23,127,127",
    "webgl_fsi_params": "0,31,30,0,31,30,0,31,30",
    "webgl_hash_webgl": None,
    "user_agent_data_brands": "Chromium,Google Chrome,Not=A?Brand",
    "user_agent_data_mobile": None,
    "navigator_connection_downlink": None,
    "navigator_connection_downlink_max": None,
    "network_info_rtt": None,
    "network_info_save_data": False,
    "network_info_rtt_type": None,
    "screen_pixel_depth": 24,
    "navigator_device_memory": 0.5,
    "navigator_languages": "en-US,fr-BE,fr,en-BE,en",
    "window_inner_width": 0,
    "window_inner_height": 0,
    "window_outer_width": 2195,
    "window_outer_height": 1195,
    "browser_detection_firefox": False,
    "browser_detection_brave": False,
    "audio_codecs": '{"ogg":"probably","mp3":"probably","wav":"probably","m4a":"maybe","aac":"probably"}',
    "video_codecs": '{"ogg":"probably","h264":"probably","webm":"probably","mpeg4v":"","mpeg4a":"","theora":""}',
    "media_query_dark_mode": True,
    "headless_browser_phantom": False,
    "headless_browser_selenium": False,
    "headless_browser_nightmare_js": False,
    "document__referrer": "https://www.roblox.com/",
    "window__ancestor_origins": ["https://www.roblox.com"],
    "window__tree_index": [0],
    "window__tree_structure": "[[]]",
    "window__location_href": "https://roblox-api.arkoselabs.com/v2/1.5.5/enforcement.fbfc14b0d793c6ef8359e0e4b4a91f67.html#476068BF-9607-4799-B53D-966BE98E2B81",
    "client_config__sitedata_location_href": "https://www.roblox.com/arkose/iframe",
    "client_config__surl": "https://roblox-api.arkoselabs.com",
    "client_config__language": None,
    "navigator_battery_charging": True,
    "audio_fingerprint": "124.04347527516074",
}


def getEnhancedFingerprint(fp, ua, opts):
    fingerprint = baseEnhancedFingerprint.copy()

    # Modify the 'fingerprint' dictionary according to your JavaScript code
    fingerprint["webgl_extensions"] = ";".join(
        filter(
            lambda _: random.random() > 0.5, fingerprint["webgl_extensions"].split(";")
        )
    )
    fingerprint["webgl_extensions_hash"] = x64hash128(
        fingerprint["webgl_extensions"], 0
    )
    fingerprint["screen_pixel_depth"] = fp["D"]
    fingerprint["navigator_languages"] = fp["L"]
    fp_S = fp["S"]
    fingerprint["window_outer_height"] = fp_S[0]
    fingerprint["window_outer_width"] = fp_S[1]
    fingerprint["window_inner_height"] = fp_S[0]
    fingerprint["window_inner_width"] = fp_S[1]
    fingerprint["browser_detection_firefox"] = bool(re.search(r"Firefox/\d+", ua))
    fingerprint["browser_detection_brave"] = bool(re.search(r"Brave/\d+", ua))
    fingerprint["media_query_dark_mode"] = random.random() > 0.9
    fingerprint["webgl_hash_webgl"] = x64hash128(
        ",".join(
            [
                v
                for k, v in fingerprint.items()
                if k.startswith("webgl_") and k != "webgl_hash_webgl"
            ]
        ),
        0,
    )
    fingerprint["client_config__language"] = opts.get("language", None)
    fingerprint[
        "window__location_href"
    ] = f"{opts.get('surl', 'https://client-api.arkoselabs.com')}/v2/1.5.5/enforcement.fbfc14b0d793c6ef8359e0e4b4a91f67.html#{opts['pkey']}"

    if "site" in opts:
        fingerprint["document__referrer"] = opts["site"]
        fingerprint["window__ancestor_origins"] = [opts["site"]]
        fingerprint["client_config__sitedata_location_href"] = opts["site"]

    fingerprint["client_config__surl"] = opts.get(
        "surl", "https://client-api.arkoselabs.com"
    )
    fingerprint["audio_fingerprint"] = str(
        124.04347527516074 + random.uniform(-0.0005, 0.0005)
    )

    return [{"key": k, "value": v} for k, v in fingerprint.items()]
