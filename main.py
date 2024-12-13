import random
import pygame
import sys
import time

class Boton:
    def __init__(self, x, y, text, font, text_color, bg_color):
        self.font = font
        self.text = font.render(text, True, text_color)
        self.bg_color = bg_color
        self.text_rect = self.text.get_rect(center=(x, y))
        self.rect = pygame.Rect(self.text_rect.x - 10, self.text_rect.y - 5,
                                self.text_rect.width + 20, self.text_rect.height + 10)
        self.enabled = True

    def draw(self, screen):
        if self.enabled:
            pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=5)
            screen.blit(self.text, self.text_rect)

    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

class Item:
    def __init__(self, image_path, position):
        self.original_image = pygame.image.load(image_path)
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=position)
        self.enabled = True

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

    def select(self, selected_image_path):
        self.selected_image = pygame.image.load(selected_image_path)
        self.image = self.selected_image

    def disable(self, disable_image_path):
        self.image = pygame.image.load(disable_image_path)
        self.enabled = False

    def reveal_goat(self):
        self.image = pygame.image.load("img/goat.png")
        self.enabled = False

    def reset(self):
        self.image = self.original_image
        self.enabled = True

def main():
    pygame.init()
    pygame.mixer.init()  # Inicializar mixer de sonido
    screen = pygame.display.set_mode((1436, 728))
    pygame.display.set_caption("Monty Hall")

    bg = pygame.image.load("img/bg.png")

    # Cargar sonidos
    door_sound = pygame.mixer.Sound("sfx/Door.mp3")
    win_sound = pygame.mixer.Sound("sfx/Win.mp3")
    lose_sound = pygame.mixer.Sound("sfx/Lose.mp3")

    # Crear tres objetos clicables
    objects = [
        Item("img/door.png", (209, 275)),
        Item("img/door.png", (618, 275)),
        Item("img/door.png", (1027, 275))
    ]

    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    # Fuentes
    font_title = pygame.font.Font(None, 72)
    font_subtitle = pygame.font.Font(None, 48)
    font_button = pygame.font.Font(None, 36)
    font_victories = pygame.font.Font(None, 36)

    # Contador de victorias
    victories = 0
    game_state = "start"
    selected_door = None
    game_result = None
    doors_content = None
    result_start_time = None
    replay_start_time = None

    # Crear botones para cambiar de puerta
    btn_yes = Boton(screen.get_width() // 2 - 50, 180, "Si", font_button, BLACK, GREEN)
    btn_no = Boton(screen.get_width() // 2 + 50, 180, "No", font_button, BLACK, RED)

    # Crear botones para volver a jugar
    btn_play_again_yes = Boton(screen.get_width() // 2 - 50, 230, "Si", font_button, BLACK, GREEN)
    btn_play_again_no = Boton(screen.get_width() // 2 + 50, 230, "No", font_button, BLACK, RED)

    while True:
        cursor_changed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "start":
                    for index, obj in enumerate(objects):
                        if obj.is_clicked(event.pos):
                            # Seleccionar puerta inicial
                            selected_door = index
                            obj.image = pygame.image.load("img/door_selected.png")
                            game_state = "show_goat"

                            # Generar contenido de puertas
                            doors_content = ["cabra", "cabra", "auto"]
                            random.shuffle(doors_content)
                            print(doors_content)

                            # Revelar una cabra en las puertas no seleccionadas
                            for i, content in enumerate(doors_content):
                                if i != selected_door and content == "cabra":
                                    objects[i].image = pygame.image.load("img/goat.png")
                                    door_sound.play()  # Reproducir sonido de puerta
                                    doors_content[i] = "abierta"  # Marcar la puerta como abierta
                                    break

                elif game_state == "show_goat":
                    # Botones para cambiar de puerta
                    if btn_yes.is_clicked(event.pos):
                        # Cambiar a la otra puerta disponible
                        for i, content in enumerate(doors_content):
                            if i != selected_door and content != "abierta":
                                selected_door = i
                                break
                        game_state = "result"
                        game_result = doors_content[selected_door] == "auto"
                        result_start_time = pygame.time.get_ticks()

                        # Mostrar contenido de la puerta final
                        if game_result:
                            objects[selected_door].image = pygame.image.load("img/car.png")
                            win_sound.play()  # Reproducir sonido de victoria
                        else:
                            objects[selected_door].image = pygame.image.load("img/goat.png")
                            lose_sound.play()  # Reproducir sonido de derrota

                        if game_result:
                            victories += 1

                    elif btn_no.is_clicked(event.pos):
                        game_state = "result"
                        game_result = doors_content[selected_door] == "auto"
                        result_start_time = pygame.time.get_ticks()

                        # Mostrar contenido de la puerta final
                        if game_result:
                            objects[selected_door].image = pygame.image.load("img/car.png")
                            win_sound.play()  # Reproducir sonido de victoria
                        else:
                            objects[selected_door].image = pygame.image.load("img/goat.png")
                            lose_sound.play()  # Reproducir sonido de derrota

                        if game_result:
                            victories += 1

                elif game_state == "result":

                    # Botones para volver a jugar
                    if btn_play_again_yes.is_clicked(event.pos):
                        # Reiniciar el juego
                        game_state = "start"
                        for obj in objects:
                            obj.reset()
                        game_result = None
                        doors_content = None
                    elif btn_play_again_no.is_clicked(event.pos):
                        pygame.quit()
                        sys.exit()

        mouse_pos = pygame.mouse.get_pos()

        # Cambiar el cursor si está sobre un objeto o botón
        cursor_changed = False
        for obj in objects:
            if obj.is_clicked(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                cursor_changed = True
                break

        if not cursor_changed:
            if btn_yes.is_clicked(mouse_pos) or btn_no.is_clicked(mouse_pos) or btn_play_again_yes.is_clicked(
                    mouse_pos) or btn_play_again_no.is_clicked(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                cursor_changed = True

        if not cursor_changed:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        screen.blit(bg, (0, 0))
        for obj in objects:
            obj.draw(screen)

        # Mostrar mensajes según el estado del juego
        if game_state == "start":
            mensaje = font_subtitle.render("Seleccione una puerta", True, WHITE)
            screen.blit(mensaje, (screen.get_width() // 2 - mensaje.get_width() // 2, 100))

        elif game_state == "show_goat":
            mensaje = font_subtitle.render("¿Desea cambiar de puerta?", True, WHITE)
            screen.blit(mensaje, (screen.get_width() // 2 - mensaje.get_width() // 2, 100))

            # Dibujar botones
            btn_yes.draw(screen)
            btn_no.draw(screen)

        elif game_state == "result":
            current_time = pygame.time.get_ticks()
            for obj in objects:
                obj.image = pygame.Surface((0, 0))  # Hacer invisible
            if current_time - result_start_time >= 5000:
                # Ocultar todos los objetos
                final_image = pygame.image.load("img/car.png") if game_result else pygame.image.load("img/goat.png")
                screen.blit(final_image, (518, 275))

                if game_result:
                    mensaje = font_title.render("¡GANASTE EL AUTO!", True, GREEN)
                else:
                    mensaje = font_title.render("¡PERDISTE!", True, RED)
                screen.blit(mensaje, (screen.get_width() // 2 - mensaje.get_width() // 2, 100))

                # Mostrar mensaje de volver a jugar
                if current_time - result_start_time >= 10000:
                    mensaje_replay = font_subtitle.render("¿Desea volver a jugar?", True, WHITE)
                    screen.blit(mensaje_replay, (screen.get_width() // 2 - mensaje_replay.get_width() // 2, 165))

                    # Dibujar botones de volver a jugar
                    btn_play_again_yes.draw(screen)
                    btn_play_again_no.draw(screen)

        # Mostrar contador de victorias
        if game_state != "result":
            victories_text = font_victories.render(f"Victorias: {victories}", True, WHITE)
            screen.blit(victories_text, (10, 10))

        pygame.display.flip()

if __name__ == "__main__":
    main()