# SPDX-FileCopyrightText: Copyright (c) 2021-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import array
import numpy as np
import imgui
from gui_utils import imgui_utils


class PerformanceWidget:
    def __init__(self, viz):
        self.viz            = viz
        self.gui_times      = [float('nan')] * 60
        self.render_times   = [float('nan')] * 30
        self.fps_limit      = 60
        self.use_vsync      = False
        self.is_async       = False
        self.force_fp32     = False

    @imgui_utils.scoped_by_object_id
    def __call__(self, show=True):
        viz = self.viz
        self.gui_times = self.gui_times[1:] + [viz.frame_delta]
        if 'render_time' in viz.result:
            self.render_times = self.render_times[1:] + [viz.result.render_time]
            del viz.result.render_time

        if show:
            imgui.text('GUI')
            imgui.same_line(viz.label_w)
            with imgui_utils.item_width(viz.font_size * 8):
                imgui.plot_lines('##gui_times', array.array('f', self.gui_times), scale_min=0)
            imgui.same_line(viz.label_w + viz.font_size * 9)
            t = [x for x in self.gui_times if x > 0]
            t = np.mean(t) if len(t) > 0 else 0
            imgui.text(f'{t*1e3:.1f} ms' if t > 0 else 'N/A')
            imgui.same_line(viz.label_w + viz.font_size * 14)
            imgui.text(f'{1/t:.1f} FPS' if t > 0 else 'N/A')
            with imgui_utils.item_width(viz.font_size * 6):
                _changed, self.fps_limit = imgui.input_int('FPS limit', self.fps_limit, flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
                self.fps_limit = min(max(self.fps_limit, 5), 1000)
            imgui.same_line(viz.label_w + viz.font_size * 9)
            _clicked, self.use_vsync = imgui.checkbox('Vertical sync', self.use_vsync)

            imgui.text('Render')
            imgui.same_line(viz.label_w)
            with imgui_utils.item_width(viz.font_size * 8):
                imgui.plot_lines('##render_times', array.array('f', self.render_times), scale_min=0)
            imgui.same_line(viz.label_w + viz.font_size * 9)
            t = [x for x in self.render_times if x > 0]
            t = np.mean(t) if len(t) > 0 else 0
            imgui.text(f'{t*1e3:.1f} ms' if t > 0 else 'N/A')
            imgui.same_line(viz.label_w + viz.font_size * 14)
            imgui.text(f'{1/t:.1f} FPS' if t > 0 else 'N/A')

        viz.set_fps_limit(self.fps_limit)
        viz.set_vsync(self.use_vsync)

