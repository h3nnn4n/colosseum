ONE_SECOND = 1000


class Config:
    # Game Settings
    game_name = "snake"
    update_mode = "SIMULTANEOUS"

    grid_width = 40
    grid_height = 40
    food_sources_to_spawn = 2
    min_food_sources = 1
    n_epochs = 100

    # Time settings
    step_time_limit = ONE_SECOND * 2
    step_limit_pool = ONE_SECOND * 20
