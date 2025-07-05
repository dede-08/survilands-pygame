#tamaños
WIDTH, HEIGHT = 1280, 720
PLAYER = 100
GRASS = 64
TREE = 64
SMALL_STONE = 32

#animaciones 
BASIC_FRAMES = 6
IDLE_DOWN = 0
IDLE_RIGHT = 1
IDLE_UP = 2
WALK_DOWN = 3
WALK_RIGHT = 4
WALK_UP = 5
FRAME_SIZE = 32
ACTION_FRAME_SIZE = 48
ANIMATION_DELAY = 100
RUNNING_ANIMATION_DELAY = 50

#colores
WHITE = (255, 255, 255) 
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)

# barras de estado
MAX_ENERGY = 100
MAX_FOOD = 100
MAX_THIRST = 100
MAX_STAMINA = 100

#colores para las barras de estado
ENERY_COLOR = (255, 255, 0) #amarillo
FOOD_COLOR = (255, 165, 0) #naranja
THIRST_COLOR = (0, 191, 255) #azul claro
STAMINA_COLOR = (124, 252, 0) #verde claro
BAR_BACKGROUND = (100, 100, 100) #gris oscuro

#intervalo de tiempo
STATUS_UPDATE_INTERVAL = 1000

#sitema dia/noche
DAY_LENGTH = 240000      #duracion del dia completo en milisegundos
DAWN_TIME = 60000        #amanecer a las 6:00
MORNING_TIME = 80000     #mañana completa a las 8:00
DUKS_TIME = 180000       #aterdecer a las 18:00
MIDNIGHT = 240000        #medianoche (00:00)
MAX_DARKNESS = 210      #nivel maximo de oscuridad (0-255)

#colores para iluminacion
NIGHT_COLOR = (20, 20, 50)          #color azul oscuro para la noche
DAY_COLOR = (255, 255, 255)         #color blanco para el dia
DAWN_DUSK_COLOR = (255, 193, 137)   #color anaranjado para el amanecer/atardecer


#velocidades de disminucion de estados}
FOOD_DECREASE_RATE = 1      #velocidad de disminucion de comida
THIRST_DECREASE_RATE = 1    #velocidad de disminucion de sed
ENERY_DECREASE_RATE = 0.005     #velocidad de disminucion de energia en estado critico
ENERY_INCREASE_RATE = 0.001     #velocidad de recuperacion de energia en estado normal
MOVEMENT_ENERGY_COST = 0.001    #energia consumida por movimiento

# nuevas constantes para correr
WALK_SPEED = 5
RUN_SPEED = 8
STAMINA_DECREASE_RATE = 0.05
STAMINA_INCREASE_RATE = 0.02
RUN_FOOD_DECREASE_MULTIPLIER = 2.0
RUN_THIRST_DECREASE_MULTIPLIER = 2.0

#inventory constants
SLOT_SIZE = 64
HOTBAR_SLOTS = 8
INVENTORY_ROWS = 4
INVENTORY_COLS = 5
MARGIN = 10

#HOTBAR position(siempre visible abajo)
HOTBAR_Y = HEIGHT - SLOT_SIZE - MARGIN
HOTBAR_X = (WIDTH - (SLOT_SIZE * HOTBAR_SLOTS)) // 2

#main inventory position (en el centro cuando esta abierto)
INVENTORY_X = (WIDTH - (SLOT_SIZE * INVENTORY_COLS)) // 2
INVENTORY_Y = (HEIGHT - (SLOT_SIZE * INVENTORY_ROWS)) // 2

#crafting constants
CRAFTING_GRID_SIZE = 2
CRAFTING_RESULT_SLOT_X = INVENTORY_X + (SLOT_SIZE * (INVENTORY_COLS + 1))
CRAFTING_RESULT_SLOT_Y = INVENTORY_Y
CRAFTING_GRID_X = INVENTORY_X + (SLOT_SIZE * (INVENTORY_COLS + 1))
CRAFTING_GRID_Y = INVENTORY_Y + SLOT_SIZE * 2

#hand slots constants
LEFT_HAND_SLOT_X = HOTBAR_X - SLOT_SIZE - MARGIN
LEFT_HAND_SLOT_Y = HOTBAR_Y
RIGHT_HAND_SLOT_X = HOTBAR_X + (SLOT_SIZE * HOTBAR_SLOTS) + MARGIN
RIGHT_HAND_SLOT_Y = HOTBAR_Y

#tools animations settings
AXE_COLS = 2
AXE_FRAMES = 2
AXE_ANIMATION_DELAY = 200
HOE_COLS = 2
HOE_FRAMES = 2
HOE_ANIMATION_DELAY = 200

#colors for inventory
SLOT_COLOR = (139, 139, 139)        #gray
SLOT_BORDER = (100, 100, 100)       #darker gray
SLOT_HOVER = (160, 160, 160)        #lighter gray


#constants for the water
WATER_COLOR = (64, 164, 223, 180)       #azul semi-transparente para el agua
WATER_MOVEMENT_MULTIPLIER = 0.5         #movimiento mas lento en agua
WATER_GENERATION_PROBABILITY = 0.3      #probabilidad de generar agua en un chunk
WATER_THIRST_RECOVERY = 20              #cantidad de sed recuperada al beber agua








