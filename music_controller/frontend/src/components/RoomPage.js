import React, { Component } from "react"

export default class Room extends Component {
    constructor(props) {
        super(props);
        this.state = {
            guestCanPause: false,
            votesToSkip: 2,
            isHost: false,
        };
        this.roomCode = this.props.match.params.roomCode;
        this.getRoomDetails();
    }

    getRoomDetails() {
        fetch("/api/get-room" + "?code=" + this.roomCode)
            .then((response) => response.json())
            .then((data) => {
                this.setState({
                    votesToSkip: data.votes_to_skip,
                    guestCanPause: data.guest_can_pause,
                    isHost: data.is_host,
                });
            });
    }

    render() {
        return (
            <div>
                <h3>{this.roomCode}</h3>
                <p>You are in a room</p>
                <p>Votes: {this.state.votesToSkip.toString()}</p>
                <p>Guests can pause: {this.state.guestCanPause.toString()}</p>
                <p>Are you the host? {this.state.isHost.toString()}</p>
            </div>
        )};
}