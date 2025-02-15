def main():
    pygame.init()
    window_width, window_height = 800, 600
    pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("River Crossing Game with ImGui")

    init_opengl(window_width, window_height)

    # Create ImGui context and the PygameRenderer.
    imgui.create_context()
    impl = PygameRenderer()
    io = imgui.get_io()
    io.display_size = (window_width, window_height)

    game = RiverCrossingGame()
    game.game_loop(impl)

if __name__ == "__main__":
    main()