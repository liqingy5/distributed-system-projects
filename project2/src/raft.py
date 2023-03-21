## Just pseudocode for now, can change later
class RaftNode:
    def __init__(self, id, peers):
        self.id = id
        self.peers = peers
        self.state = 'follower'
        # Persistent state on all servers:
        self.currentTerm = 0 ## latest term server has seen (initialized to 0 on first boot, increases monotonically)
        self.votedFor = None ## candidateId that received vote in current term (or null if none)
        self.log = [] ## log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1)
        # Volatile state on all servers:
        self.commitIndex = 0 ## index of highest log entry known to be committed (initialized to 0, increases monotonically)
        self.lastApplied = 0 ## index of highest log entry applied to state machine (initialized to 0, increases monotonically)
        # Volatile state on leaders:
        self.nextIndex = {} ## for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
        self.matchIndex = {} ## for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)
    def __str__(self):
        return 'Raft(id={}, state={}, currentTerm={}, votedFor={}, log={}, commitIndex={}, lastApplied={}, nextIndex={}, matchIndex={})'.format(
            self.id, self.state, self.currentTerm, self.votedFor, self.log, self.commitIndex, self.lastApplied, self.nextIndex, self.matchIndex)
    
    def __repr__(self):
        return self.__str__()
    
    def send(self, peer, message):
        print('Sending {} to {}'.format(message, peer))
    
    def broadcast(self, message):
        for peer in self.peers:
            self.send(peer, message)
    
    def become_follower(self, term):
        print('Becoming follower')
        self.state = 'follower'
        self.currentTerm = term
        self.votedFor = None

    def become_candidate(self):
        print('Becoming candidate')
        self.state = 'candidate'
        self.currentTerm += 1
        self.votedFor = self.id
        self.broadcast('RequestVote(term={}, candidateId={})'.format(self.currentTerm, self.id))
    
    def become_leader(self):
        print('Becoming leader')
        self.state = 'leader'
        self.broadcast('AppendEntries(term={}, leaderId={})'.format(self.currentTerm, self.id))
    
    def on_request_vote(self, term, candidate_id):
        if term < self.currentTerm:
            self.send(candidate_id, 'RequestVoteResponse(term={}, voteGranted=false)'.format(self.currentTerm))
        else:
            if self.votedFor is None or self.votedFor == candidate_id:
                self.votedFor = candidate_id
                self.send(candidate_id, 'RequestVoteResponse(term={}, voteGranted=true)'.format(self.currentTerm))
            else:
                self.send(candidate_id, 'RequestVoteResponse(term={}, voteGranted=false)'.format(self.currentTerm))
    
    def on_request_vote_response(self, term, vote_granted):
        if term > self.currentTerm:
            self.become_follower(term)

    def on_append_entries(self, term, leader_id):
        if term < self.currentTerm:
            self.send(leader_id, 'AppendEntriesResponse(term={}, success=false)'.format(self.currentTerm))
        else:
            self.become_follower(term)
            self.send(leader_id, 'AppendEntriesResponse(term={}, success=true)'.format(self.currentTerm))
    
    def on_append_entries_response(self, term, success):
        if term > self.currentTerm:
            self.become_follower(term)

    def on_timeout(self):
        if self.state == 'follower':
            self.become_candidate()
        elif self.state == 'candidate':
            self.become_candidate()
        elif self.state == 'leader':
            self.broadcast('AppendEntries(term={}, leaderId={})'.format(self.currentTerm, self.id))

    def on_message(self, message):
        if message.startswith('RequestVote'):
            term, candidate_id = message[12:-1].split(', ')
            term = int(term[5:])
            candidate_id = int(candidate_id[12:])
            self.on_request_vote(term, candidate_id)
        elif message.startswith('RequestVoteResponse'):
            term, vote_granted = message[20:-1].split(', ')
            term = int(term[5:])
            vote_granted = vote_granted[12:] == 'true'
            self.on_request_vote_response(term, vote_granted)
        elif message.startswith('AppendEntries'):
            term, leader_id = message[13:-1].split(', ')
            term = int(term[5:])
            leader_id = int(leader_id[10:])
            self.on_append_entries(term, leader_id)
        elif message.startswith('AppendEntriesResponse'):
            term, success = message[21:-1].split(', ')
            term = int(term[5:])
            success = success[8:] == 'true'
            self.on_append_entries_response(term, success)
        else:
            print('Unknown message: {}'.format(message))
    
    def tick(self):
        if self.state == 'follower':
            self.on_timeout()
        elif self.state == 'candidate':
            self.on_timeout()
        elif self.state == 'leader':
            self.on_timeout()
