class Config:
    # Game Settings
    game_name = "cherry_picker"
    update_mode = "ISOLATED"

    grid_width = 50
    grid_height = 50
    max_food_sources = 50
    take_food_max_distance = 1
    deposit_food_max_distance = 0.15
    actor_radius = 0.45
    attack_range = 5
    take_food_speed = 5
    spawn_actor_cost = 100
    make_base_cost = 500
    base_spawn_border_offset = 0.15
    n_epochs = 1000

    # Actor Settings
    actor_speed = 1
    actor_damage = 5
    actor_max_health = 50
