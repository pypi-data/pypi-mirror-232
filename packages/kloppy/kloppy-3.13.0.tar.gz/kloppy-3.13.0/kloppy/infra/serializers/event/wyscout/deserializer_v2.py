import json
import logging
from typing import Dict, List, Tuple, NamedTuple, IO

from kloppy.domain import (
    BodyPart,
    BodyPartQualifier,
    CardType,
    CounterAttackQualifier,
    Dimension,
    DuelResult,
    DuelQualifier,
    DuelType,
    EventDataset,
    GoalkeeperQualifier,
    GoalkeeperActionType,
    Ground,
    Metadata,
    Orientation,
    PassQualifier,
    PassResult,
    PassType,
    Period,
    Player,
    Point,
    Provider,
    Qualifier,
    SetPieceQualifier,
    SetPieceType,
    ShotResult,
    TakeOnResult,
    Team,
)
from kloppy.utils import performance_logging

from . import wyscout_events, wyscout_tags
from ..deserializer import EventDataDeserializer

logger = logging.getLogger(__name__)


INVALID_PLAYER = "0"


def _parse_team(raw_events, wyId: str, ground: Ground) -> Team:
    team = Team(
        team_id=wyId,
        name=raw_events["teams"][wyId]["officialName"],
        ground=ground,
    )
    team.players = [
        Player(
            player_id=str(player["playerId"]),
            team=team,
            jersey_no=None,
            first_name=player["player"]["firstName"],
            last_name=player["player"]["lastName"],
        )
        for player in raw_events["players"][wyId]
    ]
    return team


def _has_tag(raw_event, tag_id) -> bool:
    for tag in raw_event["tags"]:
        if tag["id"] == tag_id:
            return True
    return False


def _generic_qualifiers(raw_event: Dict) -> List[Qualifier]:
    qualifiers: List[Qualifier] = []

    if _has_tag(raw_event, wyscout_tags.COUNTER_ATTACK):
        qualifiers.append(CounterAttackQualifier(True))
    else:
        qualifiers.append(CounterAttackQualifier(False))

    return qualifiers


def _parse_shot(raw_event: Dict, next_event: Dict) -> Dict:
    result = None
    qualifiers = _generic_qualifiers(raw_event)
    if _has_tag(raw_event, 101):
        result = ShotResult.GOAL
    elif _has_tag(raw_event, 2101):
        result = ShotResult.BLOCKED
    elif any((_has_tag(raw_event, tag) for tag in wyscout_tags.SHOT_POST)):
        result = ShotResult.POST
    elif any(
        (_has_tag(raw_event, tag) for tag in wyscout_tags.SHOT_OFF_TARGET)
    ):
        result = ShotResult.OFF_TARGET
    elif any((_has_tag(raw_event, tag) for tag in wyscout_tags.SHOT_ON_GOAL)):
        result = ShotResult.SAVED

    if next_event["eventId"] == wyscout_events.SAVE.EVENT:
        if next_event["subEventId"] == wyscout_events.SAVE.REFLEXES:
            qualifiers.append(GoalkeeperQualifier(GoalkeeperActionType.REFLEX))
        if next_event["subEventId"] == wyscout_events.SAVE.SAVE_ATTEMPT:
            qualifiers.append(
                GoalkeeperQualifier(GoalkeeperActionType.SAVE_ATTEMPT)
            )

    return {
        "result": result,
        "result_coordinates": Point(
            x=float(raw_event["positions"][1]["x"]),
            y=float(raw_event["positions"][1]["y"]),
        )
        if len(raw_event["positions"]) > 1
        else None,
        "qualifiers": qualifiers,
    }


def _pass_qualifiers(raw_event) -> List[Qualifier]:
    qualifiers = _generic_qualifiers(raw_event)

    if raw_event["subEventId"] == wyscout_events.PASS.CROSS:
        qualifiers.append(PassQualifier(PassType.CROSS))
    elif raw_event["subEventId"] == wyscout_events.PASS.HAND:
        qualifiers.append(PassQualifier(PassType.HAND_PASS))
    elif raw_event["subEventId"] == wyscout_events.PASS.HEAD:
        qualifiers.append(PassQualifier(PassType.HEAD_PASS))
        qualifiers.append(BodyPartQualifier(BodyPart.HEAD))
    elif raw_event["subEventId"] == wyscout_events.PASS.HIGH:
        qualifiers.append(PassQualifier(PassType.HIGH_PASS))
    elif raw_event["subEventId"] == wyscout_events.PASS.LAUNCH:
        qualifiers.append(PassQualifier(PassType.LAUNCH))
    elif raw_event["subEventId"] == wyscout_events.PASS.SIMPLE:
        qualifiers.append(PassQualifier(PassType.SIMPLE_PASS))
    elif raw_event["subEventId"] == wyscout_events.PASS.SMART:
        qualifiers.append(PassQualifier(PassType.SMART_PASS))

    if _has_tag(raw_event, wyscout_tags.LEFT_FOOT):
        qualifiers.append(BodyPartQualifier(BodyPart.LEFT_FOOT))
    elif _has_tag(raw_event, wyscout_tags.RIGHT_FOOT):
        qualifiers.append(BodyPartQualifier(BodyPart.RIGHT_FOOT))

    return qualifiers


def _parse_pass(raw_event: Dict, next_event: Dict) -> Dict:
    pass_result = None

    if _has_tag(raw_event, wyscout_tags.ACCURATE):
        pass_result = PassResult.COMPLETE
    elif _has_tag(raw_event, wyscout_tags.NOT_ACCURATE):
        pass_result = PassResult.INCOMPLETE

    if next_event:
        if next_event["eventId"] == wyscout_events.OFFSIDE.EVENT:
            pass_result = PassResult.OFFSIDE
        if next_event["eventId"] == wyscout_events.INTERRUPTION.EVENT:
            if (
                next_event["subEventId"]
                == wyscout_events.INTERRUPTION.BALL_OUT
            ):
                pass_result = PassResult.OUT

    return {
        "result": pass_result,
        "qualifiers": _pass_qualifiers(raw_event),
        "receive_timestamp": None,
        "receiver_player": None,
        "receiver_coordinates": Point(
            x=float(raw_event["positions"][1]["x"]),
            y=float(raw_event["positions"][1]["y"]),
        )
        if len(raw_event["positions"]) > 1
        else None,
    }


def _parse_clearance(raw_event: Dict) -> Dict:
    qualifiers = _generic_qualifiers(raw_event)
    return {"result": None, "qualifiers": qualifiers}


def _parse_goalkeeper_save(raw_event) -> List[Qualifier]:
    qualifiers = _generic_qualifiers(raw_event)
    goalkeeper_qualifiers = []
    if not _has_tag(raw_event, wyscout_tags.GOAL):
        goalkeeper_qualifiers.append(
            GoalkeeperQualifier(value=GoalkeeperActionType.SAVE)
        )
    else:
        goalkeeper_qualifiers.append(
            GoalkeeperQualifier(value=GoalkeeperActionType.SAVE_ATTEMPT)
        )
    if raw_event["subEventId"] == wyscout_events.SAVE.REFLEXES:
        goalkeeper_qualifiers.append(
            GoalkeeperQualifier(value=GoalkeeperActionType.REFLEX)
        )
    qualifiers.extend(goalkeeper_qualifiers)
    return {"result": None, "qualifiers": qualifiers}


def _parse_foul(raw_event: Dict) -> Dict:
    qualifiers = _generic_qualifiers(raw_event)
    return {
        "result": None,
        "qualifiers": qualifiers,
    }


def _parse_card(raw_event: Dict) -> Dict:
    qualifiers = _generic_qualifiers(raw_event)
    card_type = None
    if _has_tag(raw_event, wyscout_tags.RED_CARD):
        card_type = CardType.RED
    elif _has_tag(raw_event, wyscout_tags.YELLOW_CARD):
        card_type = CardType.FIRST_YELLOW
    elif _has_tag(raw_event, wyscout_tags.SECOND_YELLOW_CARD):
        card_type = CardType.SECOND_YELLOW

    return {"result": None, "qualifiers": qualifiers, "card_type": card_type}


def _parse_recovery(raw_event: Dict) -> Dict:
    qualifiers = _generic_qualifiers(raw_event)
    return {
        "result": None,
        "qualifiers": qualifiers,
    }


def _parse_ball_out(raw_event: Dict) -> Dict:
    qualifiers = _generic_qualifiers(raw_event)
    return {"result": None, "qualifiers": qualifiers}


def _parse_set_piece(raw_event: Dict, next_event: Dict) -> Dict:
    qualifiers = _generic_qualifiers(raw_event)

    result = {}

    if raw_event["subEventId"] in wyscout_events.FREE_KICK.PASS_TYPES:
        result = _parse_pass(raw_event, next_event)
        if raw_event["subEventId"] == wyscout_events.FREE_KICK.GOAL_KICK:
            qualifiers.append(SetPieceQualifier(SetPieceType.GOAL_KICK))
        elif raw_event["subEventId"] == wyscout_events.FREE_KICK.THROW_IN:
            qualifiers.append(SetPieceQualifier(SetPieceType.THROW_IN))
            qualifiers.append(PassQualifier(PassType.HAND_PASS))
        elif raw_event["subEventId"] in [
            wyscout_events.FREE_KICK.FREE_KICK,
            wyscout_events.FREE_KICK.FREE_KICK_CROSS,
        ]:
            qualifiers.append(SetPieceQualifier(SetPieceType.FREE_KICK))
        elif raw_event["subEventId"] == wyscout_events.FREE_KICK.CORNER:
            qualifiers.append(SetPieceQualifier(SetPieceType.CORNER_KICK))
    elif raw_event["subEventId"] in wyscout_events.FREE_KICK.SHOT_TYPES:
        result = _parse_shot(raw_event, next_event)
        if raw_event["subEventId"] == wyscout_events.FREE_KICK.FREE_KICK_SHOT:
            qualifiers.append(SetPieceQualifier(SetPieceType.FREE_KICK))
        elif raw_event["subEventId"] == wyscout_events.FREE_KICK.PENALTY:
            qualifiers.append(SetPieceQualifier(SetPieceType.PENALTY))

    result["qualifiers"] = qualifiers
    return result


def _parse_duel(raw_event: Dict) -> Dict:
    qualifiers = _generic_qualifiers(raw_event)
    duel_qualifiers = []

    sub_event_id = raw_event["subEventId"]

    if sub_event_id == wyscout_events.DUEL.AERIAL:
        duel_qualifiers.extend(
            [
                DuelQualifier(value=DuelType.LOOSE_BALL),
                DuelQualifier(value=DuelType.AERIAL),
            ]
        )
    elif sub_event_id in [
        wyscout_events.DUEL.GROUND_ATTACKING,
        wyscout_events.DUEL.GROUND_DEFENDING,
    ]:
        duel_qualifiers.extend([DuelQualifier(value=DuelType.GROUND)])
    elif sub_event_id == wyscout_events.DUEL.GROUND_LOOSE_BALL:
        duel_qualifiers.extend(
            [
                DuelQualifier(value=DuelType.LOOSE_BALL),
                DuelQualifier(value=DuelType.GROUND),
            ]
        )

    if _has_tag(raw_event, wyscout_tags.SLIDING_TACKLE):
        duel_qualifiers.extend([DuelQualifier(value=DuelType.SLIDING_TACKLE)])

    qualifiers.extend(duel_qualifiers)

    result = None
    if _has_tag(raw_event, wyscout_tags.WON):
        result = DuelResult.WON
    elif _has_tag(raw_event, wyscout_tags.LOST):
        result = DuelResult.LOST
    elif _has_tag(raw_event, wyscout_tags.NEUTRAL):
        result = DuelResult.NEUTRAL

    return {"result": result, "qualifiers": qualifiers}


def _players_to_dict(players: List[Player]):
    return {player.player_id: player for player in players}


class WyscoutInputs(NamedTuple):
    event_data: IO[bytes]


class WyscoutDeserializerV2(EventDataDeserializer[WyscoutInputs]):
    @property
    def provider(self) -> Provider:
        return Provider.WYSCOUT

    def deserialize(self, inputs: WyscoutInputs) -> EventDataset:
        transformer = self.get_transformer(length=100, width=100)

        with performance_logging("load data", logger=logger):
            raw_events = json.load(inputs.event_data)
            for event in raw_events["events"]:
                if "eventId" not in event:
                    event["eventId"] = event["eventName"]
                if "subEventId" not in event:
                    event["subEventId"] = event.get("subEventName")

        periods = []

        with performance_logging("parse data", logger=logger):
            home_team_id, away_team_id = raw_events["teams"].keys()
            home_team = _parse_team(raw_events, home_team_id, Ground.HOME)
            away_team = _parse_team(raw_events, away_team_id, Ground.AWAY)
            teams = {home_team_id: home_team, away_team_id: away_team}
            players = dict(
                [
                    (wyId, _players_to_dict(team.players))
                    for wyId, team in teams.items()
                ]
            )

            events = []

            for idx, raw_event in enumerate(raw_events["events"]):
                next_event = None
                if (idx + 1) < len(raw_events["events"]):
                    next_event = raw_events["events"][idx + 1]

                team_id = str(raw_event["teamId"])
                player_id = str(raw_event["playerId"])
                period_id = int(raw_event["matchPeriod"].replace("H", ""))

                if len(periods) == 0 or periods[-1].id != period_id:
                    periods.append(
                        Period(
                            id=period_id,
                            start_timestamp=0,
                            end_timestamp=0,
                        )
                    )

                generic_event_args = {
                    "event_id": raw_event["id"],
                    "raw_event": raw_event,
                    "coordinates": Point(
                        x=float(raw_event["positions"][0]["x"]),
                        y=float(raw_event["positions"][0]["y"]),
                    ),
                    "team": teams[team_id],
                    "player": players[team_id][player_id]
                    if player_id != INVALID_PLAYER
                    else None,
                    "ball_owning_team": None,
                    "ball_state": None,
                    "period": periods[-1],
                    "timestamp": raw_event["eventSec"],
                }

                event = None
                if raw_event["eventId"] == wyscout_events.SHOT.EVENT:
                    shot_event_args = _parse_shot(raw_event, next_event)
                    event = self.event_factory.build_shot(
                        **shot_event_args, **generic_event_args
                    )
                elif raw_event["eventId"] == wyscout_events.PASS.EVENT:
                    pass_event_args = _parse_pass(raw_event, next_event)
                    event = self.event_factory.build_pass(
                        **pass_event_args, **generic_event_args
                    )
                elif raw_event["eventId"] == wyscout_events.FOUL.EVENT:
                    foul_event_args = _parse_foul(raw_event)
                    event = self.event_factory.build_foul_committed(
                        **foul_event_args, **generic_event_args
                    )
                    if any(
                        (_has_tag(raw_event, tag) for tag in wyscout_tags.CARD)
                    ):
                        card_event_args = _parse_card(raw_event)
                        event = self.event_factory.build_card(
                            **card_event_args, **generic_event_args
                        )
                elif raw_event["eventId"] == wyscout_events.INTERRUPTION.EVENT:
                    ball_out_event_args = _parse_ball_out(raw_event)
                    event = self.event_factory.build_ball_out(
                        **ball_out_event_args, **generic_event_args
                    )
                elif raw_event["eventId"] == wyscout_events.SAVE.EVENT:
                    goalkeeper_save_args = _parse_goalkeeper_save(raw_event)
                    event = self.event_factory.build_goalkeeper_event(
                        **goalkeeper_save_args, **generic_event_args
                    )
                elif raw_event["eventId"] == wyscout_events.FREE_KICK.EVENT:
                    set_piece_event_args = _parse_set_piece(
                        raw_event, next_event
                    )
                    if (
                        raw_event["subEventId"]
                        in wyscout_events.FREE_KICK.PASS_TYPES
                    ):
                        event = self.event_factory.build_pass(
                            **set_piece_event_args, **generic_event_args
                        )
                    elif (
                        raw_event["subEventId"]
                        in wyscout_events.FREE_KICK.SHOT_TYPES
                    ):
                        event = self.event_factory.build_shot(
                            **set_piece_event_args, **generic_event_args
                        )

                elif (
                    raw_event["eventId"] == wyscout_events.OTHERS_ON_BALL.EVENT
                ):
                    if (
                        raw_event["subEventId"]
                        == wyscout_events.OTHERS_ON_BALL.CLEARANCE
                    ):
                        clearance_event_args = _parse_clearance(raw_event)
                        event = self.event_factory.build_clearance(
                            **clearance_event_args,
                            **generic_event_args,
                        )
                    elif (
                        raw_event["subEventId"]
                        == wyscout_events.OTHERS_ON_BALL.TOUCH
                    ) & (_has_tag(raw_event, wyscout_tags.MISSED_BALL)):
                        miscontrol_event_args = {
                            "result": None,
                            "qualifiers": _generic_qualifiers(raw_event),
                        }
                        event = self.event_factory.build_miscontrol(
                            **miscontrol_event_args,
                            **generic_event_args,
                        )
                    else:
                        recovery_event_args = _parse_recovery(raw_event)
                        event = self.event_factory.build_recovery(
                            **recovery_event_args, **generic_event_args
                        )
                elif raw_event["eventId"] == wyscout_events.DUEL.EVENT:
                    duel_event_args = _parse_duel(raw_event)
                    event = self.event_factory.build_duel(
                        **duel_event_args, **generic_event_args
                    )
                elif raw_event["eventId"] not in [
                    wyscout_events.SAVE.EVENT,
                    wyscout_events.OFFSIDE.EVENT,
                ]:
                    # The events SAVE and OFFSIDE are already merged with PASS and SHOT events
                    qualifiers = _generic_qualifiers(raw_event)
                    event = self.event_factory.build_generic(
                        result=None,
                        qualifiers=qualifiers,
                        **generic_event_args,
                    )

                if event and self.should_include_event(event):
                    events.append(transformer.transform_event(event))

        metadata = Metadata(
            teams=[home_team, away_team],
            periods=periods,
            pitch_dimensions=transformer.get_to_coordinate_system().pitch_dimensions,
            score=None,
            frame_rate=None,
            orientation=Orientation.BALL_OWNING_TEAM,
            flags=None,
            provider=Provider.WYSCOUT,
            coordinate_system=transformer.get_to_coordinate_system(),
        )

        return EventDataset(metadata=metadata, records=events)
