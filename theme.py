theme = {}

# label
theme.update({
    "label": {
        "colours": {
            "normal_text": "#000",
        },
        "font": {
            "name": "Arial",
            "size": "14"
        },
        "misc": {
            "text_horiz_alignment": "left"
        }
    },
    "#model_label": {
        "font": {
            "name": "Arial",
            "size": "18"
        },
    }
})

# button
theme.update({
    "button": {
        "colours": {
            "normal_bg": "#F3F3F3",
            "hovered_bg": "rgb(229,243,255)",
            "disabled_bg": "#F3F3F3",
            "selected_bg": "rgb(204,232,255)",
            "active_bg": "rgb(204,232,255)",
            "normal_text": "#000",
            "hovered_text": "#000",
            "selected_text": "#000",
            "disabled_text": "#A6A6A6",
            "active_text": "#000",
            "normal_border": "#CCCCCC",
            "hovered_border": "#A6A6A6",
            "disabled_border": "#CCCCCC",
            "selected_border": "#A6A6A6",
            "active_border": "#0078D7",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
            "border_width": "1",
            "shadow_width": "0",
            "tool_tip_delay": "1.0",
            "text_horiz_alignment": "center",
            "text_vert_alignment": "center",
            "text_horiz_alignment_padding": "10",
            "text_vert_alignment_padding": "5",
            "text_shadow_size": "0",
            "text_shadow_offset": "0,0"
        }
    },
    '@panel2_up_button': {
    },
    '#close_button': {
        "colours": {
            "normal_bg": "#0000",
            "hovered_bg": "#ff1212",
            "active_bg": "#e81123",
            "normal_text": "#000",
            "hovered_text": "#FFF",
            "active_text": "#FFF"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "0,0,0,0",
            "border_width": "0",
            "shadow_width": "0",
        }
    },
    '#minimize_button': {
        "colours": {
            "normal_bg": "#0000",
            "hovered_bg": "#FFFA",
            "active_bg": "#FFFC",
            "normal_text": "#000",
            "hovered_text": "#000",
            "active_text": "#000"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "0,0,0,0",
            "border_width": "0",
            "shadow_width": "0",
        }
    },
    "#logo_button": {
        "colours": {
            "normal_bg": "#0000",
            "hovered_bg": "#0000",
            "active_bg": "#0000",
            "normal_text": "#0000",
            "hovered_text": "#0000",
            "active_text": "#0000"
        },
        "images": {
            "normal_image": {
                "path": "ui/DX.png",
                "sub_surface_rect": "0,0,30,30"
            },

        },
    },
    "#buttom_bar": {
        "colours": {
            "normal_bg": "#0000",
            "hovered_bg": "#0000",
            "active_bg": "#0000",
            "normal_text": "#000",
            "hovered_text": "#000",
            "active_text": "#000"
        },
        "misc": {
            "shape": "rectangle",
            "border_width": "0",
            "shadow_width": "1"
        }
    }
})

# panel
theme.update({
    "panel": {
        "colours": {
            "dark_bg": "#F9F9F9",
            "normal_border": "#888"
        },
    }
})

# UISelectionList
theme.update({
    "selection_list": {
        "colours": {
            "dark_bg": "#F9F9F9",
            "normal_border": "#999999"

        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
        }
    },
    "selection_list.@selection_list_item": {
        "colours": {
            "dark_bg": "#F9F9F9",
            "normal_border": "#999999"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
        }
    },
    # UIButton
    "@RightClick.#item_list_item": {
        "misc": {
            "text_horiz_alignment": "left",
            "text_horiz_alignment_padding": "10",
        }
    }
})

# drop_down_menu
theme.update({
    "drop_down_menu": {
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
            "open_button_width": "0"
        }
    },
    "drop_down_menu.button": {
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
        }
    },
    "drop_down_menu.#drop_down_options_list": {
        "colours": {
            "dark_bg": "#F9F9F9",
            "normal_border": "#999999"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
        }
    },
    "drop_down_menu.#drop_down_options_list.button": {
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
        }
    },
})

# UIVerticalScrollBar
theme.update({
    "vertical_scroll_bar": {
        "colours": {
            "normal_bg": "rgb(205, 205, 205)",
            "hovered_bg": "rgb(166, 166, 166)",
            "selected_bg": "#25292e",
            "active_bg": "rgb(96, 96, 96)",
            "dark_bg": "#f0f0f0",
            "normal_text": "#c5cbd8",
            "hovered_text": "#FFFFFF",
            "selected_text": "#FFFFFF",
            "disabled_text": "#6d736f"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "10",
            "enable_arrow_buttons": "0"
        }
    },
    "vertical_scroll_bar.#sliding_button": {
        "colours": {
            "normal_bg": "rgb(205, 205, 205)",
            "hovered_bg": "rgb(166, 166, 166)",
            "selected_bg": "#25292e",
            "active_bg": "rgb(96, 96, 96)",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "10",
            "border_width": "1"
        }
    }
})

# text_box
theme.update({
    "text_box": {
        "colours": {
            "dark_bg": "#ced1ff,#e9efc8,30",
            "selected_bg": "#00F",
            "normal_border": "rgb(130, 170, 255)",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "10",
            "border_width": "2"
        }
    },
    "passrate_textbox": {
        "font": {
            "name": "Arial",
            "size": "50"
        },
    }

})

# UISelectionList
theme.update({
    "selection_list": {
        "colours": {
            "dark_bg": "#FFF",
            "normal_border": "#999"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
            "border_width": "1",
            "list_item_height": "25"
        }
    }
    # UIVerticalScrollBar

})

# UIWindow
theme.update({
    "window": {
        "colours": {
            "dark_bg": "#FFFF",
            "normal_border": "#999"
        },

        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
            "title_bar_height": "25"
        }
    },
    "window.#title_bar": {
        "colours": {
            "normal_bg": "#e4ebf499",
            "hovered_bg": "#f4fbf4BB",
            "active_bg": "#e4ebf4",
            "normal_text": "#000",
            "hovered_text": "#000",
            "active_text": "#000"
            #         "normal_bg": "#F3F3F3",
            #         "hovered_bg": "rgb(229,243,255)",
            #         "disabled_bg": "#F3F3F3",
            #         "selected_bg": "rgb(204,232,255)",
            #         "active_bg": "rgb(204,232,255)",
            #         "normal_text": "#000",
            #         "hovered_text": "#000",
            #         "selected_text": "#000",
            #         "disabled_text": "#A6A6A6",
            #         "active_text": "#000",
            #         "normal_border": "#CCCCCC",
            #         "hovered_border": "#A6A6A6",
            #         "disabled_border": "#CCCCCC",
            #         "selected_border": "#A6A6A6",
            #         "active_border": "#0078D7",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5,0,0,0",

        }
    },
    "window.#close_button": {
        "colours": {
            "normal_bg": "#e4ebf4",
            "hovered_bg": "#ff1212",
            "active_bg": "#e81123",
            "normal_text": "#000",
            "hovered_text": "#FFF",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "0,5,0,0",
        }
    }
})

# UIFileDialog
theme.update({
    # UITextEntryLine
    "file_dialog.#file_path_text_line": {
        "colours": {
            "dark_bg": "#FF93",
            "selected_bg": "#0078d7",
            "normal_text": "#000",
            "selected_text": "#FFF",
        }},
    # UISelectionList
    "#file_dialog.#file_display_list": {
        "colours": {
            "dark_bg": "#FFF",
            "normal_border": "#999"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
            "list_item_height": "25"
        }
    },
    # UIButton
    "#file_dialog.#file_display_list.#directory_list_item": {
        "colours": {
            "normal_bg": "#FF93",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
        }
    },
    # UIButton
    "file_dialog.#file_display_list.#file_list_item": {
        "colours": {
            "normal_bg": "#FFF0",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "5",
        }
    }
})

if __name__ == '__main__':
    import auto_inspection

    auto_inspection.main()
