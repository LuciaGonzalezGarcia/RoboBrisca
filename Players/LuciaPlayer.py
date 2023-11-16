from Game.Action import Action
from Game.Card import Card
from Game.CardCollection import CardCollection
from Game.ForwardModel import ForwardModel
from Players.MyHeuristic import MyHeuristic
from Players.Player import Player


class LuciaPlayer(Player):

    def __init__(self):
        self.forward_model = ForwardModel()
        self.heuristic = MyHeuristic()
        self.unknown_cards = CardCollection()    # Una lista de cartas desconocidas.

    def think(self, observation, budget):

        # Quito las cartas conocidas de la lista
        self.unknown_cards.clear()
        self.create_deck(self.unknown_cards)

        for card in observation.playing_cards.get_cards():
            self.unknown_cards.remove(card)
        for card in observation.won_cards[0].get_cards():
            self.unknown_cards.remove(card)
        for card in observation.won_cards[1].get_cards():
            self.unknown_cards.remove(card)
        for card in observation.won_cards[2].get_cards():
            self.unknown_cards.remove(card)
        for card in observation.won_cards[3].get_cards():
            self.unknown_cards.remove(card)
        my_cards = observation.hands[observation.turn].get_cards()
        for card in my_cards:
            self.unknown_cards.remove(card)
        if observation.trump_card in self.unknown_cards.get_cards():
            self.unknown_cards.remove(observation.trump_card)

        # Decido que acción realizar. Dependiendo de que turno sea, la estrategia será diferente.
        list_actions = observation.get_list_actions()
        if len(list_actions) == 1:
            return list_actions[0]

        player_id = observation.turn
        if player_id == 0:
            return self.player0(observation)
        elif player_id == 1:
            return self.player1(observation)
        elif player_id == 2:
            return self.player2(observation)
        else:
            return self.player3(observation)

    def player0(self, observation):
        # El primer jugador, como no tiene información sobre la jugada, tirará la peor carta que tenga y asi no se
        # arriesga a perderla con el siguiente enemigo y reserva las mejores cartas para otros turnos.

        my_cards = observation.hands[0].get_cards()
        best_card = None
        best_value = 1000
        best_probability = 1000

        for card in my_cards:

            value = self.calcular_importancia(observation, card)    # Calculo la importancia de mi carta
            prob_derrota = self.calcular_prob_derrota(observation, card)   # Calculo la probabilidad de derrota

            # Elijo la carta mas baja y con mayor probabilidad de derrota (Me guardo las mejores cartas)
            if value < best_value or (value == best_value and prob_derrota > best_probability):
                best_value = value
                best_probability = prob_derrota
                best_card = card

        return Action(best_card)

    def player1(self, observation):
        # El segundo jugador analiza la carta jugada por el anterior jugador:
        # - Si tiene alguna carta que pueda ganarle, tirará la más bajita que tenga, evitando arriesgarse a perderla
        # con el siguiente enemigo y reservando las mejores cartas para otros turnos.
        # - Si no tiene ninguna carta que pueda ganarle, tirará la peor carta que tenga para no perder ninguna buena
        # y reservarse las mejores para otros turnos.

        my_cards = observation.hands[1].get_cards()
        best_card = None
        best_value = 1000
        best_probability = 0
        best_relation = 10000
        best_points = -1000

        for card in my_cards:

            value = self.calcular_importancia(observation, card)  # Calculo la importancia de mi carta
            prob_derrota = self.calcular_prob_derrota(observation, card)  # Calculo la probabilidad de derrota

            # Miro si tengo posibilidad de ganar
            new_obs = observation.clone()
            points = self.forward_model.play(new_obs, Action(card), self.heuristic)

            # Si tengo posibilidad de ganar
            if points >= 0:
                relation = value / prob_derrota
                if relation < best_relation:
                    best_relation = relation
                    best_points = points
                    best_card = card

            # Si no tengo posibilidad de ganar
            elif best_points < 0:
                if value < best_value or (value == best_value and prob_derrota > best_probability):
                    best_value = value
                    best_probability = prob_derrota
                    best_points = points
                    best_card = card

        return Action(best_card)

    def player2(self, observation):
        # El tercer jugador analiza las cartas jugadas por los anteriores jugadores:
        # - Si tiene alguna carta que pueda ganar, tirará la más bajita que tenga, evitando arriesgarse a perderla
        # con el siguiente enemigo y reservando las mejores cartas para otros turnos.
        # - Si no tiene ninguna carta que pueda ganar, tirará la peor carta que tenga para no perder ninguna buena
        # y reservarse las mejores para otros turnos.

        my_cards = observation.hands[2].get_cards()
        best_card = None
        best_value = 1000
        best_probability = 0
        best_relation = 10000
        best_points = -1000

        for card in my_cards:

            value = self.calcular_importancia(observation, card)  # Calculo la importancia de mi carta
            prob_derrota = self.calcular_prob_derrota(observation, card)  # Calculo la probabilidad de derrota

            # Miro si tengo posibilidad de ganar
            new_obs = observation.clone()
            points = self.forward_model.play(new_obs, Action(card), self.heuristic)

            # Si tengo posibilidad de ganar
            if points >= 0:
                relation = value / prob_derrota
                if relation < best_relation:
                    best_relation = relation
                    best_points = points
                    best_card = card

            # Si no tengo posibilidad de ganar
            elif best_points < 0:
                if value < best_value or (value == best_value and prob_derrota > best_probability):
                    best_value = value
                    best_probability = prob_derrota
                    best_points = points
                    best_card = card

        return Action(best_card)

    def player3(self, observation):
        # El último jugador conoce toda la información de la partida. Analiza las cartas jugadas por los anteriores
        # jugadores:
        # - Si tiene alguna carta que pueda ganar, tirará la que más puntos tenga para ganar lo máximo.
        # - Si no tiene ninguna carta que pueda ganar, tirará la peor carta que tenga para no perder ninguna buena y
        # darle al enemigo los mínimos puntos posibles. Además, se reserva las mejores cartas para otros turnos.

        my_cards = observation.hands[3].get_cards()
        best_card = None
        best_points = -1000
        worst_points = 1000

        for card in my_cards:

            new_obs = observation.clone()
            points = self.forward_model.play(new_obs, Action(card), self.heuristic)

            if points >= 0:
                if points > best_points:
                    best_points = points
                    best_card = card

            elif best_points < 0:
                if points < worst_points:
                    worst_points = points
                    best_card = card

            # result = porcent_derrota * value
            # if result < best_value:
            #     best_value = result
            #     best_card = card

        return Action(best_card)

    def calcular_importancia(self, observation, card):
        if card.card_type == observation.trump_card.card_type:
            if card.card_number in [1, 3]:
                return 1
            elif card.card_number in [12, 11, 10]:
                return 0.9
            else:
                return 0.8
        else:
            if card.card_number in [1, 3]:
                return 0.7
            elif card.card_number in [12, 11, 10]:
                return 0.5
            else:
                return 0.2

    def calcular_prob_derrota(self, observation, card):
        better_cards = 0
        for other_card in self.unknown_cards.get_cards():
            if other_card.card_type == card.card_type:
                if other_card.card_number > card.card_number:
                    better_cards += 1
            elif other_card.card_type == observation.trump_card.card_type:
                better_cards += 1

        prob_derrota = better_cards / self.unknown_cards.len()
        if prob_derrota == 0:
            return 0.001
        return prob_derrota

    def create_deck(self, deck):
        l_types = ["O", "E", "C", "B"]
        l_numbers = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
        deck.clear()
        for card_type in l_types:
            for number in l_numbers:
                deck.add_card(Card(card_type, number))

        deck.shuffle()

    def __str__(self):
        return "LuciaPlayer"
