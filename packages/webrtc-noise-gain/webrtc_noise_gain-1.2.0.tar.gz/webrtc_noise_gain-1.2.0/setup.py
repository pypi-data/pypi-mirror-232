import platform
from pathlib import Path

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

_DIR = Path(__file__).parent
_SOURCE_DIR = _DIR / "webrtc-audio-processing"
_WEBRTC_DIR = _SOURCE_DIR / "webrtc-audio-processing-1"

__version__ = "1.2.0"

# webrtc/
#   rtc_base/
#   api/
#   system_wrappers/
#   common_audio
# third_party/
#   pffft/
#   rnnoise/
# modules/
#   audio_coding
#   audio_processing/
base_sources = [
    "checks.cc",
    "event.cc",
    "event_tracer.cc",
    "experiments/field_trial_parser.cc",
    "logging.cc",
    "memory/aligned_malloc.cc",
    "platform_thread.cc",
    "platform_thread_types.cc",
    "race_checker.cc",
    "string_encode.cc",
    "string_to_number.cc",
    "string_utils.cc",
    "strings/string_builder.cc",
    "synchronization/mutex.cc",
    "synchronization/rw_lock_wrapper.cc",
    "synchronization/yield.cc",
    "synchronization/yield_policy.cc",
    "system/file_wrapper.cc",
    "time_utils.cc",
    "zero_memory.cc",
] + [
    # posix
    "synchronization/rw_lock_posix.cc",
]

api_sources = [
    "audio/audio_frame.cc",
    "audio/channel_layout.cc",
    "audio/echo_canceller3_config.cc",
    "audio_codecs/audio_decoder.cc",
    "audio_codecs/audio_encoder.cc",
    "rtp_headers.cc",
    "rtp_packet_info.cc",
    "task_queue/task_queue_base.cc",
    "units/data_rate.cc",
    "units/data_size.cc",
    "units/frequency.cc",
    "units/time_delta.cc",
    "units/timestamp.cc",
    "video/color_space.cc",
    "video/hdr_metadata.cc",
    "video/video_content_type.cc",
    "video/video_timing.cc",
]

system_wrappers_sources = [
    "source/cpu_features.cc",
    "source/field_trial.cc",
    "source/metrics.cc",
    "source/sleep.cc",
]

common_audio_sources = [
    "audio_converter.cc",
    "audio_util.cc",
    "channel_buffer.cc",
    "fir_filter_c.cc",
    "fir_filter_factory.cc",
    "real_fourier.cc",
    "real_fourier_ooura.cc",
    "resampler/push_resampler.cc",
    "resampler/push_sinc_resampler.cc",
    "resampler/resampler.cc",
    "resampler/sinc_resampler.cc",
    "resampler/sinusoidal_linear_chirp_source.cc",
    "ring_buffer.c",
    "signal_processing/auto_correlation.c",
    "signal_processing/auto_corr_to_refl_coef.c",
    "signal_processing/complex_bit_reverse.c",
    "signal_processing/complex_fft.c",
    "signal_processing/copy_set_operations.c",
    "signal_processing/cross_correlation.c",
    "signal_processing/division_operations.c",
    "signal_processing/dot_product_with_scale.cc",
    "signal_processing/downsample_fast.c",
    "signal_processing/filter_ar.c",
    "signal_processing/filter_ar_fast_q12.c",
    "signal_processing/energy.c",
    "signal_processing/filter_ma_fast_q12.c",
    "signal_processing/get_hanning_window.c",
    "signal_processing/get_scaling_square.c",
    "signal_processing/ilbc_specific_functions.c",
    "signal_processing/levinson_durbin.c",
    "signal_processing/lpc_to_refl_coef.c",
    "signal_processing/min_max_operations.c",
    "signal_processing/randomization_functions.c",
    "signal_processing/real_fft.c",
    "signal_processing/refl_coef_to_lpc.c",
    "signal_processing/resample_48khz.c",
    "signal_processing/resample_by_2.c",
    "signal_processing/resample_by_2_internal.c",
    "signal_processing/resample.c",
    "signal_processing/resample_fractional.c",
    "signal_processing/spl_init.c",
    "signal_processing/spl_inl.c",
    "signal_processing/splitting_filter.c",
    "signal_processing/spl_sqrt.c",
    "signal_processing/sqrt_of_one_minus_x_squared.c",
    "signal_processing/vector_scaling_operations.c",
    "smoothing_filter.cc",
    "third_party/ooura/fft_size_128/ooura_fft.cc",
    "third_party/ooura/fft_size_256/fft4g.cc",
    "third_party/spl_sqrt_floor/spl_sqrt_floor.c",
    "vad/vad.cc",
    "vad/vad_core.c",
    "vad/vad_filterbank.c",
    "vad/vad_gmm.c",
    "vad/vad_sp.c",
    "vad/webrtc_vad.c",
    "wav_file.cc",
    "wav_header.cc",
    "window_generator.cc",
]

isac_vad_sources = [
    "codecs/isac/main/source/filter_functions.c",
    "codecs/isac/main/source/isac_vad.c",
    "codecs/isac/main/source/pitch_estimator.c",
    "codecs/isac/main/source/pitch_filter.c",
]

webrtc_audio_coding_sources = [
    "codecs/isac/main/source/arith_routines.c",
    "codecs/isac/main/source/arith_routines_hist.c",
    "codecs/isac/main/source/arith_routines_logist.c",
    "codecs/isac/main/source/audio_decoder_isac.cc",
    "codecs/isac/main/source/audio_encoder_isac.cc",
    "codecs/isac/main/source/bandwidth_estimator.c",
    "codecs/isac/main/source/crc.c",
    "codecs/isac/main/source/decode_bwe.c",
    "codecs/isac/main/source/decode.c",
    "codecs/isac/main/source/encode.c",
    "codecs/isac/main/source/encode_lpc_swb.c",
    "codecs/isac/main/source/entropy_coding.c",
    "codecs/isac/main/source/filterbanks.c",
    "codecs/isac/main/source/intialize.c",
    "codecs/isac/main/source/isac.c",
    "codecs/isac/main/source/lattice.c",
    "codecs/isac/main/source/lpc_analysis.c",
    "codecs/isac/main/source/lpc_gain_swb_tables.c",
    "codecs/isac/main/source/lpc_shape_swb12_tables.c",
    "codecs/isac/main/source/lpc_shape_swb16_tables.c",
    "codecs/isac/main/source/lpc_tables.c",
    "codecs/isac/main/source/pitch_gain_tables.c",
    "codecs/isac/main/source/pitch_lag_tables.c",
    "codecs/isac/main/source/spectrum_ar_model_tables.c",
    "codecs/isac/main/source/transform.c",
]

webrtc_audio_processing_sources = [
    "aec_dump/null_aec_dump_factory.cc",
    "aec3/adaptive_fir_filter.cc",
    "aec3/adaptive_fir_filter_erl.cc",
    "aec3/aec3_common.cc",
    "aec3/aec3_fft.cc",
    "aec3/aec_state.cc",
    "aec3/alignment_mixer.cc",
    "aec3/api_call_jitter_metrics.cc",
    "aec3/block_buffer.cc",
    "aec3/block_delay_buffer.cc",
    "aec3/block_framer.cc",
    "aec3/block_processor.cc",
    "aec3/block_processor_metrics.cc",
    "aec3/clockdrift_detector.cc",
    "aec3/coarse_filter_update_gain.cc",
    "aec3/comfort_noise_generator.cc",
    "aec3/decimator.cc",
    "aec3/dominant_nearend_detector.cc",
    "aec3/downsampled_render_buffer.cc",
    "aec3/echo_audibility.cc",
    "aec3/echo_canceller3.cc",
    "aec3/echo_path_delay_estimator.cc",
    "aec3/echo_path_variability.cc",
    "aec3/echo_remover.cc",
    "aec3/echo_remover_metrics.cc",
    "aec3/erle_estimator.cc",
    "aec3/erl_estimator.cc",
    "aec3/fft_buffer.cc",
    "aec3/filter_analyzer.cc",
    "aec3/frame_blocker.cc",
    "aec3/fullband_erle_estimator.cc",
    "aec3/matched_filter.cc",
    "aec3/matched_filter_lag_aggregator.cc",
    "aec3/moving_average.cc",
    "aec3/refined_filter_update_gain.cc",
    "aec3/render_buffer.cc",
    "aec3/render_delay_buffer.cc",
    "aec3/render_delay_controller.cc",
    "aec3/render_delay_controller_metrics.cc",
    "aec3/render_signal_analyzer.cc",
    "aec3/residual_echo_estimator.cc",
    "aec3/reverb_decay_estimator.cc",
    "aec3/reverb_frequency_response.cc",
    "aec3/reverb_model.cc",
    "aec3/reverb_model_estimator.cc",
    "aec3/signal_dependent_erle_estimator.cc",
    "aec3/spectrum_buffer.cc",
    "aec3/stationarity_estimator.cc",
    "aec3/subband_erle_estimator.cc",
    "aec3/subband_nearend_detector.cc",
    "aec3/subtractor.cc",
    "aec3/subtractor_output_analyzer.cc",
    "aec3/subtractor_output.cc",
    "aec3/suppression_filter.cc",
    "aec3/suppression_gain.cc",
    "aec3/transparent_mode.cc",
    "aecm/aecm_core.cc",
    "aecm/aecm_core_c.cc",
    "aecm/echo_control_mobile.cc",
    "agc/agc.cc",
    "agc/agc_manager_direct.cc",
    "agc/legacy/analog_agc.cc",
    "agc/legacy/digital_agc.cc",
    "agc/loudness_histogram.cc",
    "agc/utility.cc",
    "agc2/adaptive_agc.cc",
    "agc2/adaptive_digital_gain_applier.cc",
    "agc2/adaptive_mode_level_estimator_agc.cc",
    "agc2/adaptive_mode_level_estimator.cc",
    "agc2/agc2_testing_common.cc",
    "agc2/biquad_filter.cc",
    "agc2/compute_interpolated_gain_curve.cc",
    "agc2/down_sampler.cc",
    "agc2/fixed_digital_level_estimator.cc",
    "agc2/gain_applier.cc",
    "agc2/interpolated_gain_curve.cc",
    "agc2/limiter.cc",
    "agc2/limiter_db_gain_curve.cc",
    "agc2/noise_level_estimator.cc",
    "agc2/noise_spectrum_estimator.cc",
    "agc2/rnn_vad/auto_correlation.cc",
    "agc2/rnn_vad/common.cc",
    "agc2/rnn_vad/features_extraction.cc",
    "agc2/rnn_vad/lp_residual.cc",
    "agc2/rnn_vad/pitch_search.cc",
    "agc2/rnn_vad/pitch_search_internal.cc",
    "agc2/rnn_vad/rnn.cc",
    "agc2/rnn_vad/spectral_features.cc",
    "agc2/rnn_vad/spectral_features_internal.cc",
    "agc2/saturation_protector.cc",
    "agc2/signal_classifier.cc",
    "agc2/vad_with_level.cc",
    "agc2/vector_float_frame.cc",
    "audio_buffer.cc",
    "audio_processing_builder_impl.cc",
    "audio_processing_impl.cc",
    "echo_control_mobile_impl.cc",
    "echo_detector/circular_buffer.cc",
    "echo_detector/mean_variance_estimator.cc",
    "echo_detector/moving_max.cc",
    "echo_detector/normalized_covariance_estimator.cc",
    "gain_control_impl.cc",
    "gain_controller2.cc",
    "high_pass_filter.cc",
    "include/aec_dump.cc",
    "include/audio_frame_proxies.cc",
    "include/audio_processing.cc",
    "include/audio_processing_statistics.cc",
    "include/config.cc",
    "level_estimator.cc",
    "logging/apm_data_dumper.cc",
    "ns/fast_math.cc",
    "ns/histograms.cc",
    "ns/noise_estimator.cc",
    "ns/noise_suppressor.cc",
    "ns/ns_fft.cc",
    "ns/prior_signal_model.cc",
    "ns/prior_signal_model_estimator.cc",
    "ns/quantile_noise_estimator.cc",
    "ns/signal_model.cc",
    "ns/signal_model_estimator.cc",
    "ns/speech_probability_estimator.cc",
    "ns/suppression_params.cc",
    "ns/wiener_filter.cc",
    "optionally_built_submodule_creators.cc",
    "residual_echo_detector.cc",
    "rms_level.cc",
    "splitting_filter.cc",
    "three_band_filter_bank.cc",
    "transient/file_utils.cc",
    "transient/moving_moments.cc",
    "transient/transient_detector.cc",
    "transient/transient_suppressor_impl.cc",
    "transient/wpd_node.cc",
    "transient/wpd_tree.cc",
    "typing_detection.cc",
    "utility/cascaded_biquad_filter.cc",
    "utility/delay_estimator.cc",
    "utility/delay_estimator_wrapper.cc",
    "utility/pffft_wrapper.cc",
    "vad/gmm.cc",
    "vad/pitch_based_vad.cc",
    "vad/pitch_internal.cc",
    "vad/pole_zero_filter.cc",
    "vad/standalone_vad.cc",
    "vad/vad_audio_proc.cc",
    "vad/vad_circular_buffer.cc",
    "vad/voice_activity_detector.cc",
    "voice_detection.cc",
]

pffft_sources = [
    "src/pffft.c",
]

rnnoise_sources = [
    "src/rnn_vad_weights.cc",
]

common_cflags = [
    "-DWEBRTC_LIBRARY_IMPL",
    "-DWEBRTC_ENABLE_SYMBOL_EXPORT",
    "-DNDEBUG",
    "-DWEBRTC_APM_DEBUG_DUMP=0",
    "-D_GNU_SOURCE",
]

fft_sources = ["fft.c"]

# -----------------------------------------------------------------------------

libraries = []
system = platform.system().lower()
machine = platform.machine().lower()
system_cflags = []
machine_cflags = []

have_neon = True

if system == "linux":
    system_cflags += ["-DWEBRTC_LINUX", "-DWEBRTC_THREAD_RR", "-DWEBRTC_POSIX"]
elif system == "darwin":
    system_cflags += ["-DWEBRTC_MAC"]
    machine = "arm64"  # assume cross-compiling
    have_neon = False
elif system == "windows":
    system_cflags += [
        "-DWEBRTC_WIN",
        "-D_WIN32",
        "-U__STRICT_ANSI__",
        "-D__STDC_FORMAT_MACROS=1",
        "'-DNOMINMAX'",
        "'-D_USE_MATH_DEFINES'",
    ]
    libraries += ["winmm"]
else:
    raise ValueError(f"Unsupported system: {system}")

if machine in ("aarch64", "armv8", "arm64"):
    # Assume neon
    machine_cflags += ["-DWEBRTC_ARCH_ARM64"]

    if have_neon:
        machine_cflags += ["-DWEBRTC_HAS_NEON"]
        common_audio_sources += [
            "fir_filter_neon.cc",
            "resampler/sinc_resampler_neon.cc",
            "signal_processing/cross_correlation_neon.c",
            "signal_processing/downsample_fast_neon.c",
            "signal_processing/min_max_operations_neon.c",
            "third_party/ooura/fft_size_128/ooura_fft_neon.cc",
        ]
        webrtc_audio_processing_sources += [
            "aecm/aecm_core_neon.cc",
        ]
elif machine in ("x86_64", "amd64", "x86", "i386", "i686"):
    machine_cflags += [
        "-DWEBRTC_ARCH_X86_FAMILY",
        "-DWEBRTC_ENABLE_AVX2",
        "-msse2",
        "-mavx2",
        "-mfma",
    ]
    webrtc_audio_processing_sources += [
        "aec3/adaptive_fir_filter_avx2.cc",
        "aec3/adaptive_fir_filter_erl_avx2.cc",
        "aec3/fft_data_avx2.cc",
        "aec3/matched_filter_avx2.cc",
        "aec3/vector_math_avx2.cc",
    ]
    common_audio_sources += [
        "fir_filter_sse.cc",
        "resampler/sinc_resampler_sse.cc",
        "third_party/ooura/fft_size_128/ooura_fft_sse2.cc",
        #
        "fir_filter_avx2.cc",
        "resampler/sinc_resampler_avx2.cc",
    ]
elif machine in ("armv7", "armv7l"):
    # Assume neon
    machine_cflags += ["-DWEBRTC_ARCH_ARM_V7"]
    if have_neon:
        machine_cflags += ["-DWEBRTC_HAS_NEON", "-mfpu=neon"]
        common_audio_sources += [
            "fir_filter_neon.cc",
            "resampler/sinc_resampler_neon.cc",
            "signal_processing/cross_correlation_neon.c",
            "signal_processing/downsample_fast_neon.c",
            "signal_processing/min_max_operations_neon.c",
            "third_party/ooura/fft_size_128/ooura_fft_neon.cc",
        ]
        webrtc_audio_processing_sources += [
            "aecm/aecm_core_neon.cc",
        ]
elif machine in ("armv6", "armhf", "armv6l"):
    machine_cflags += ["-DWEBRTC_ARCH_ARM", "-DPFFFT_SIMD_DISABLE"]
    common_audio_sources += [
        "signal_processing/filter_ar_fast_q12.c",
    ]
else:
    raise ValueError(f"Unsupported machine: {machine}")

# -----------------------------------------------------------------------------

ext_modules = [
    Pybind11Extension(
        name="webrtc_noise_gain_cpp",
        sources=[str(_DIR / "python.cpp")]
        + [str(_WEBRTC_DIR / "rtc_base" / f) for f in base_sources]
        + [str(_WEBRTC_DIR / "api" / f) for f in api_sources]
        + [str(_WEBRTC_DIR / "system_wrappers" / f) for f in system_wrappers_sources]
        + [
            str(_WEBRTC_DIR / "modules" / "audio_coding" / f)
            for f in webrtc_audio_coding_sources + isac_vad_sources
        ]
        + [
            str(_WEBRTC_DIR / "modules" / "audio_processing" / f)
            for f in webrtc_audio_processing_sources
        ]
        + [
            str(_WEBRTC_DIR / "modules" / "third_party" / "fft" / f)
            for f in fft_sources
        ]
        + [str(_WEBRTC_DIR / "third_party" / "pffft" / f) for f in pffft_sources]
        + [str(_WEBRTC_DIR / "third_party" / "rnnoise" / f) for f in rnnoise_sources]
        + [str(_WEBRTC_DIR / "common_audio" / f) for f in common_audio_sources],
        extra_compile_args=common_cflags + system_cflags + machine_cflags,
        define_macros=[("VERSION_INFO", __version__)],
        include_dirs=[
            str(_SOURCE_DIR),
            str(_WEBRTC_DIR),
            str(_SOURCE_DIR / "subprojects" / "abseil-cpp-20230125.1"),
        ],
        cxx_std=17,
        libraries=libraries,
    ),
]


setup(
    name="webrtc_noise_gain",
    version=__version__,
    author="Michael Hansen",
    author_email="mike@rhasspy.org",
    url="https://github.com/rhasspy/webrtc-noise-gain",
    description="Noise suppression and automatic gain with webrtc",
    long_description="",
    packages=["webrtc_noise_gain"],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)
