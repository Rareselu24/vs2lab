import random
import logging
from const2PC import *
import stablelog

class Participant:
    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log("participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.state = INIT

    @staticmethod
    def _do_work():
        return LOCAL_ABORT if random.random() > 2/3 else LOCAL_SUCCESS

    def _enter_state(self, state):
        self.stable_log.info(state)
        self.logger.info(f"Participant {self.participant} entered state {state}.")
        self.state = state

    def _elect_new_coordinator(self):
        # Simple deterministic coordinator election - choose lowest ID
        participants = sorted(list(self.all_participants))
        return participants[0]

    def _handle_coordinator_failure(self):
        if self.state == INIT:
            self._enter_state(ABORT)
            return LOCAL_ABORT

        new_coordinator = self._elect_new_coordinator()
        if new_coordinator == self.participant:
            # I am the new coordinator
            self.channel.send_to(self.all_participants, STATE_REQUEST)
            states = {}
            for _ in range(len(self.all_participants) - 1):
                msg = self.channel.receive_from(self.all_participants, TIMEOUT)
                if msg:
                    states[msg[0]] = msg[1]

            if PRECOMMIT in states.values() or self.state == PRECOMMIT:
                decision = GLOBAL_COMMIT
            else:
                decision = GLOBAL_ABORT
            
            self.channel.send_to(self.all_participants, decision)
            return decision
        else:
            # Wait for new coordinator's decision
            msg = self.channel.receive_from({new_coordinator}, TIMEOUT)
            return msg[1] if msg else LOCAL_ABORT

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self._enter_state(INIT)

    def run(self):
        # Wait for vote request
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)

        if not msg:
            decision = self._handle_coordinator_failure()
        else:
            assert msg[1] == VOTE_REQUEST
            decision = self._do_work()

            if decision == LOCAL_ABORT:
                self.channel.send_to(self.coordinator, VOTE_ABORT)
                self._enter_state(ABORT)
            else:
                self._enter_state(READY)
                self.channel.send_to(self.coordinator, VOTE_COMMIT)

                # Wait for prepare commit
                msg = self.channel.receive_from(self.coordinator, TIMEOUT)
                if not msg:
                    decision = self._handle_coordinator_failure()
                else:
                    if msg[1] == PREPARE_COMMIT:
                        self._enter_state(PRECOMMIT)
                        self.channel.send_to(self.coordinator, READY_COMMIT)

                        # Wait for global commit
                        msg = self.channel.receive_from(self.coordinator, TIMEOUT)
                        if not msg:
                            decision = self._handle_coordinator_failure()
                        else:
                            decision = msg[1]
                    else:
                        decision = msg[1]  # Should be GLOBAL_ABORT

        # Final state transition
        if decision == GLOBAL_COMMIT:
            self._enter_state(COMMIT)
        else:
            self._enter_state(ABORT)

        return f"Participant {self.participant} terminated in state {self.state}."
