class Config:
    # Game Settings
    game_name = "food_catcher"
    update_mode = "SIMULTANEOUS"

    grid_width = 40
    grid_height = 40
    max_food_sources = 10
    take_food_max_distance = 1
    deposit_food_max_distance = 0.15
    actor_radius = 0.45
    attack_range = 5
    take_food_speed = 5
    spawn_actor_cost = 100
    make_base_cost = 500
    base_spawn_border_offset = 0.15
    n_epochs = 10000

    # Actor Settings
    actor_speed = 1
    actor_damage = 5
    actor_max_health = 50

    # Time settings
    step_time_limit = 200  # 200 ms
    step_limit_pool = 2000  # 2 seconds
