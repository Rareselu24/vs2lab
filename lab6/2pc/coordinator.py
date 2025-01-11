import random
import logging
import stablelog
from const2PC import *

class Coordinator:
    def __init__(self, chan):
        self.channel = chan
        self.coordinator = self.channel.join('coordinator')
        self.participants = []
        self.stable_log = stablelog.create_log("coordinator-" + self.coordinator)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Coordinator")
        self.state = None

    def _enter_state(self, state):
        self.stable_log.info(state)
        self.logger.info(f"Coordinator {self.coordinator} entered state {state}.")
        self.state = state

    def init(self):
        self.channel.bind(self.coordinator)
        self._enter_state(INIT)
        self.participants = self.channel.subgroup('participant')

        def run(self):
            # Reduce crash probability in INIT state
            if random.random() > 0.9:  # Changed from 3/4
                return "Coordinator crashed in state INIT."

            # Phase 1a: Request votes
            self._enter_state(WAIT)
            self.channel.send_to(self.participants, VOTE_REQUEST)

            # Reduce crash probability in WAIT state
            if random.random() > 0.9:  # Changed from 2/3
                return "Coordinator crashed in state WAIT."
        # Phase 1b: Collect votes
        yet_to_receive = list(self.participants)
        while len(yet_to_receive) > 0:
            msg = self.channel.receive_from(self.participants, TIMEOUT)
            
            if (not msg) or (msg[1] == VOTE_ABORT):
                reason = "timeout" if not msg else "local_abort from " + msg[0]
                self._enter_state(ABORT)
                self.channel.send_to(self.participants, GLOBAL_ABORT)
                return f"Coordinator {self.coordinator} terminated in state ABORT. Reason: {reason}."
            
            else:
                assert msg[1] == VOTE_COMMIT
                yet_to_receive.remove(msg[0])

        # Phase 2a: Send prepare commit
        self._enter_state(PRECOMMIT)
        self.channel.send_to(self.participants, PREPARE_COMMIT)

        # Phase 2b: Collect ready commits
        yet_to_receive = list(self.participants)
        while len(yet_to_receive) > 0:
            msg = self.channel.receive_from(self.participants, TIMEOUT)
            if msg and msg[1] == READY_COMMIT:
                yet_to_receive.remove(msg[0])
            elif not msg:
                # In PRECOMMIT state, proceed even if participant fails
                yet_to_receive.remove(msg[0])

        # Phase 3: Send global commit
        self._enter_state(COMMIT)
        self.channel.send_to(self.participants, GLOBAL_COMMIT)
        return f"Coordinator {self.coordinator} terminated in state COMMIT."
