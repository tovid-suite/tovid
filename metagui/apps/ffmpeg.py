#! /usr/bin/env python
# ffmpeg.py

"""
usage: ffmpeg [[infile options] -i infile]... {[outfile options] outfile}...
Hyper fast Audio and Video encoder

Main options:
-L                  show license
-h                  show help
-version            show version
-formats            show available formats, codecs, protocols, ...
-f fmt              force format
-img img_fmt        force image format
-i filename         input file name
-y                  overwrite output files
-t duration         set the recording time
-fs limit_size      set the limit file size
-ss time_off        set the start time offset
-itsoffset time_off  set the input ts offset
-title string       set the title
-timestamp time     set the timestamp
-author string      set the author
-copyright string   set the copyright
-comment string     set the comment
-v verbose          control amount of logging
-target type        specify target file type ("vcd", "svcd", "dvd", "dv", "pal-vcd", "ntsc-svcd", ...)
-dframes number     set the number of data frames to record
-scodec codec       force subtitle codec ('copy' to copy stream)
-newsubtitle        add a new subtitle stream to the current output stream
-slang code         set the ISO 639 language code (3 letters) of the current subtitle stream
"""

from metagui import *

video = Panel("Video options",
    Panel("Bitrate",
          Number('-b', "Bitrate", None,
                 "Desired target video bitrate", 0, 10000,
                 units="kbits/sec"),
          Number('-bt', "Tolerance", None,
                 "Video bitrate tolerance",
                 units="kbits/sec"),
          Number('-maxrate', "Max tolerance", None,
                 "Maximum video bitrate tolerance",
                 units="kbits/sec"),
          Number('-minrate', "Min tolerance", None,
                 "Minimum video bitrate tolerance",
                 units="kbits/sec")
    ),

    Number('-vframes', "Frames", None,
           "Number of video frames to record",
           0, 999999),
    Text('-r', "Frame rate", None,
        "Frame rate (Hz, fraction, or abbreviation)"),
    Text('-s', "Size", None,
         "Frame size (WxH or abbreviation)"),
    Text('-aspect', "Aspect ratio", None,
         "W:H or decimal aspect ratio (ex. 4:3 or 1.333, 16:9 or 1.777)"),
    Panel("Cropping",
          Number('-croptop', "Top", 0,
                 "Pixels to crop from top", 0, 1000),
          Number('-cropbottom', "Bottom", 0,
                 "Pixels to crop from bottom", 0, 1000),
          Number('-cropleft', "Left", 0,
                 "Pixels to crop from left side", 0, 1000),
          Number('-cropright', "Right", 0,
                 "Pixels to crop from right side", 0, 1000)
    ),
    Panel("Padding",
          Color('-padcolor', "Color", '000000',
                "Color of padding"),
          Number('-padtop', "Top", 0,
                 "Pixels of padding on top", 0, 1000),
          Number('-padbottom', "Bottom", 0,
                 "Pixels of padding on bottom", 0, 1000),
          Number('-padleft', "Left", 0,
                 "Pixels of padding on left side", 0, 1000),
          Number('-padright', "Right", 0,
                 "Pixels of padding on right side", 0, 1000)
    )
)

drops = Dropdowns("Video options",
    Flag('-vn', "Disable video", False),
    Number('-bufsize', "Buffer size", None,
           "Rate control buffer size", 0, 1000, units='kilobytes'),
    Choice('-vcodec', "Video codec", None,
         "Force video codec ('copy' to copy stream)",
         "copy|mpeg2|divx|madeup",
         style='dropdown'),
    Flag('-sameq', "Keep quality", False,
         "Use the same video quality as source (implies VBR)"),
    Number('-pass', "Pass", 1,
           "Which pass to do (for two-pass encoding)", 1, 2),
    Filename('-passlogfile', "2-pass log file", None,
             "Where to write the log for 2-pass encoding"),
    Flag('-newvideo', "New video stream", False,
         "Add a new video stream to the current output stream")
)

app = Application('ffmpeg', [drops])

"""
Advanced Video options:
-pix_fmt format     set pixel format
-g gop_size         set the group of picture size
-intra              use only intra frames
-vdt n              discard threshold
-qscale q           use fixed video quantiser scale (VBR)
-qmin q             min video quantiser scale (VBR)
-qmax q             max video quantiser scale (VBR)
-lmin lambda        min video lagrange factor (VBR)
-lmax lambda        max video lagrange factor (VBR)
-mblmin q           min macroblock quantiser scale (VBR)
-mblmax q           max macroblock quantiser scale (VBR)
-qdiff q            max difference between the quantiser scale (VBR)
-qblur blur         video quantiser scale blur (VBR)
-qsquish squish     how to keep quantiser between qmin and qmax (0 = clip, 1 = use differentiable function)
-qcomp compression  video quantiser scale compression (VBR)
-rc_init_cplx complexity  initial complexity for 1-pass encoding
-b_qfactor factor   qp factor between p and b frames
-i_qfactor factor   qp factor between p and i frames
-b_qoffset offset   qp offset between p and b frames
-i_qoffset offset   qp offset between p and i frames
-ibias bias         intra quant bias
-pbias bias         inter quant bias
-rc_eq equation     set rate control equation
-rc_override override  rate control override for specific intervals
-me method          set motion estimation method
-me_threshold       motion estimaton threshold
-mb_threshold       macroblock threshold
-bf frames          use 'frames' B frames
-preme              pre motion estimation
-bug param          workaround not auto detected encoder bugs
-strict strictness  how strictly to follow the standards
-deinterlace        deinterlace pictures
-psnr               calculate PSNR of compressed frames
-vstats             dump video coding statistics to file
-vhook module       insert video processing module
-intra_matrix matrix  specify intra matrix coeffs
-inter_matrix matrix  specify inter matrix coeffs
-top                top=1/bottom=0/auto=-1 field first
-sc_threshold threshold  scene change threshold
-me_range range     limit motion vectors range (1023 for DivX player)
-dc precision       intra_dc_precision
-mepc factor (1.0 = 256)  motion estimation bitrate penalty compensation
-vtag fourcc/tag    force video tag/fourcc
-skip_threshold threshold  frame skip threshold
-skip_factor factor  frame skip factor
-skip_exp exponent  frame skip exponent
-genpts             generate pts
-qphist             show QP histogram
"""

"""
Audio options:
-aframes number     set the number of audio frames to record
-ab bitrate         set audio bitrate (in kbit/s)
-aq quality         set audio quality (codec-specific)
-ar rate            set audio sampling rate (in Hz)
-ac channels        set number of audio channels
-an                 disable audio
-acodec codec       force audio codec ('copy' to copy stream)
-vol volume         change audio volume (256=normal)
-newaudio           add a new audio stream to the current output stream
-alang code         set the ISO 639 language code (3 letters) of the current audio stream

Advanced Audio options:
-atag fourcc/tag    force audio tag/fourcc
"""

"""
Subtitle options:
-scodec codec       force subtitle codec ('copy' to copy stream)
-newsubtitle        add a new subtitle stream to the current output stream
-slang code         set the ISO 639 language code (3 letters) of the current subtitle stream

Audio/Video grab options:
-vd device          set video grab device
-vc channel         set video grab channel (DV1394 only)
-tvstd standard     set television standard (NTSC, PAL (SECAM))
-ad device          set audio device
-grab format        request grabbing using
-gd device          set grab device

Advanced options:
-map file:stream[:syncfile:syncstream]  set input stream mapping
-map_meta_data outfile:infile  set meta data information of outfile from infile
-benchmark          add timings for benchmarking
-dump               dump each input packet
-hex                when dumping packets, also dump the payload
-re                 read input at native frame rate
-loop               loop (current only works with images)
-loop_output        number of times to loop output in formats that support looping (0 loops forever)
-threads count      thread count
-vsync              video sync method
-async              audio sync method
-vglobal            video global header storage type
-copyts             copy timestamps
-shortest           finish encoding within shortest input
-ps size            set packet size in bits
-error rate         error rate
-muxrate rate       set mux rate
-packetsize size    set packet size
-muxdelay seconds   set the maximum demux-decode delay
-muxpreload seconds  set the initial demux-decode delay
"""


"""
AVCodecContext AVOptions:
-bit_rate          E.VA.
-bit_rate_tolerance E.V..
-flags             EDVA.
-mv4               E.V.. use four motion vector by macroblock (mpeg4)
-obmc              E.V.. use overlapped block motion compensation (h263+)
-qpel              E.V.. use 1/4 pel motion compensation
-loop              E.V.. use loop filter
-gmc               E.V.. use gmc
-mv0               E.V.. always try a mb with mv=<0,0>
-part              E.V.. use data partitioning
-gray              EDV.. only decode/encode grayscale
-psnr              E.V.. error[?] variables will be set during encoding
-naq               E.V.. normalize adaptive quantization
-ildct             E.V.. use interlaced dct
-low_delay         .DV.. force low delay
-alt               E.V.. enable alternate scantable (mpeg2/mpeg4)
-trell             E.V.. use trellis quantization
-bitexact          EDVAS use only bitexact stuff (except (i)dct)
-aic               E.V.. h263 advanced intra coding / mpeg4 ac prediction
-umv               E.V.. use unlimited motion vectors
-cbp               E.V.. use rate distortion optimization for cbp
-qprd              E.V.. use rate distortion optimization for qp selection
-aiv               E.V.. h263 alternative inter vlc
-slice             E.V..
-ilme              E.V.. interlaced motion estimation
-scan_offset       E.V.. will reserve space for svcd scan offset user data
-cgop              E.V.. closed gop
-fast              E.V.. allow non spec compliant speedup tricks
-sgop              E.V.. strictly enforce gop size
-noout             E.V.. skip bitstream encoding
-local_header      E.V.. place global headers at every keyframe instead of in extradata
-me_method         E.V..
-gop_size          E.V..
-cutoff            E..A. set cutoff bandwidth
-qcompress         E.V..
-qblur             E.V..
-qmin              E.V..
-qmax              E.V..
-max_qdiff         E.V..
-max_b_frames      E.V..
-b_quant_factor    E.V..
-rc_strategy       E.V..
-b_strategy        E.V..
-hurry_up          .DV..
-bugs              .DV..
-autodetect        .DV..
-old_msmpeg4       .DV..
-xvid_ilace        .DV..
-ump4              .DV..
-no_padding        .DV..
-amv               .DV..
-ac_vlc            .DV..
-qpel_chroma       .DV..
-std_qpel          .DV..
-qpel_chroma2      .DV..
-direct_blocksize  .DV..
-edge              .DV..
-hpel_chroma       .DV..
-dc_clip           .DV..
-ms                .DV..
-lelim             E.V.. single coefficient elimination threshold for luminance (negative values also consider dc coefficient)
-celim             E.V.. single coefficient elimination threshold for chrominance (negative values also consider dc coefficient)
-strict            E.V..
-very              E.V..
-strict            E.V..
-normal            E.V..
-inofficial        E.V..
-experimental      E.V..
-b_quant_offset    E.V..
-er                .DV..
-careful           .DV..
-compliant         .DV..
-aggressive        .DV..
-very_aggressive   .DV..
-mpeg_quant        E.V..
-rc_qsquish        E.V..
-rc_qmod_amp       E.V..
-rc_qmod_freq      E.V..
-rc_eq             E.V..
-rc_max_rate       E.V..
-rc_min_rate       E.V..
-rc_buffer_size    E.V..
-rc_buf_aggressivity E.V..
-i_quant_factor    E.V..
-i_quant_offset    E.V..
-rc_initial_cplx   E.V..
-dct               E.V..
-auto              E.V..
-fastint           E.V..
-int               E.V..
-mmx               E.V..
-mlib              E.V..
-altivec           E.V..
-faan              E.V..
-lumi_mask         E.V.. lumimasking
-tcplx_mask        E.V.. temporal complexity masking
-scplx_mask        E.V.. spatial complexity masking
-p_mask            E.V.. inter masking
-dark_mask         E.V.. darkness masking
-idct              EDV..
-auto              EDV..
-int               EDV..
-simple            EDV..
-simplemmx         EDV..
-libmpeg2mmx       EDV..
-ps2               EDV..
-mlib              EDV..
-arm               EDV..
-altivec           EDV..
-sh4               EDV..
-simplearm         EDV..
-h264              EDV..
-vp3               EDV..
-ipp               EDV..
-xvidmmx           EDV..
-ec                .DV..
-guess_mvs         .DV..
-deblock           .DV..
-pred              E.V.. prediction method
-left              E.V..
-plane             E.V..
-median            E.V..
-aspect            E.V..
-debug             EDVAS print specific debug info
-pict              .DV..
-rc                E.V..
-bitstream         .DV..
-mb_type           .DV..
-qp                .DV..
-mv                .DV..
-dct_coeff         .DV..
-skip              .DV..
-startcode         .DV..
-pts               .DV..
-er                .DV..
-mmco              .DV..
-bugs              .DV..
-vis_qp            .DV..
-vis_mb_type       .DV..
-vismv             .DV.. visualize motion vectors
-pf                .DV..
-bf                .DV..
-bb                .DV..
-mb_qmin           E.V..
-mb_qmax           E.V..
-cmp               E.V.. full pel me compare function
-subcmp            E.V.. sub pel me compare function
-mbcmp             E.V.. macroblock compare function
-ildctcmp          E.V.. interlaced dct compare function
-dia_size          E.V..
-last_pred         E.V..
-preme             E.V..
-precmp            E.V.. pre motion estimation compare function
-sad               E.V..
-sse               E.V..
-satd              E.V..
-dct               E.V..
-psnr              E.V..
-bit               E.V..
-rd                E.V..
-zero              E.V..
-vsad              E.V..
-vsse              E.V..
-nsse              E.V..
-w53               E.V..
-w97               E.V..
-dctmax            E.V..
-chroma            E.V..
-pre_dia_size      E.V..
-subq              E.V.. sub pel motion estimation quality
-me_range          E.V..
-ibias             E.V..
-pbias             E.V..
-coder             E.V..
-vlc               E.V.. variable length coder / huffman coder
-ac                E.V.. arithmetic coder
-context           E.V.. context model
-mbd               E.V..
-simple            E.V..
-bits              E.V..
-rd                E.V..
-sc_threshold      E.V..
-lmin              E.V.. min lagrange factor
-lmax              E.V.. max lagrange factor
-nr                E.V.. noise reduction
-rc_init_occupancy E.V..
-inter_threshold   E.V..
-flags2            EDVA.
-antialias         .DV..
-auto              .DV..
-fastint           .DV..
-int               .DV..
-float             .DV..
-qns               E.V.. quantizer noise shaping
-thread_count      EDV..
-dc                E.V..
-nssew             E.V.. nsse weight
-skip_top          .DV..
-skip_bottom       .DV..
-profile           E.VA.
-unknown           E.VA.
-level             E.VA.
-unknown           E.VA.
-lowres            .DV..
-frame_skip_threshold E.V..
-frame_skip_factor E.V..
-frame_skip_exp    E.V..
-skipcmp           E.V.. frame skip compare function
-border_mask       E.V..
-mb_lmin           E.V..
-mb_lmax           E.V..
-me_penalty_compensation E.V..
-bidir_refine      E.V..
-brd_scale         E.V..
-crf               E.V..
-cqp               E.V..
-keyint_min        E.V..
-refs              E.V..
-chromaoffset      E.V..
-bframebias        E.V..
-trellis           E.V..
-directpred        E.V..
-bpyramid          E.V..
-wpred             E.V..
-mixed_refs        E.V..
-8x8dct            E.V..
-fastpskip         E.V..
-aud               E.V..
-brdo              E.V..
-complexityblur    E.V..
-deblockalpha      E.V..
-deblockbeta       E.V..
-partitions        E.V..
-parti4x4          E.V..
-parti8x8          E.V..
-partp4x4          E.V..
-partp8x8          E.V..
-partb8x8          E.V..
-sc_factor         E.V..
"""


gui = GUI('ffmpeg metagui', [app])
gui.run()

