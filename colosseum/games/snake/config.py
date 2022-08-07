ONE_SECOND = 1000


class Config:
    # Game Settings
    game_name = "snake"
    update_mode = "SIMULTANEOUS"

    grid_width = 10
    grid_height = 10
    food_sources_to_spawn = 5
    min_food_sources = 1
    n_epochs = 25

    # Time settings
    step_time_limit = ONE_SECOND * 2
    step_limit_pool = ONE_SECOND * 20
