import React, { Component } from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import CreateRoomPage from "./CreateRoomPage";
import MusicPlayer from "./MusicPlayer";

export default class Room extends Component {
    constructor(props) {
        super(props);
        this.state = {
            guestCanPause: false,
            votesToSkip: 2,
            isHost: false,
            showSettings: false,
            spotifyAuthenticated: false,
            song: {},
        };
        this.roomCode = this.props.match.params.roomCode;
        this.leaveButtonPressed = this.leaveButtonPressed.bind(this);
        this.updateShowSettings = this.updateShowSettings.bind(this);
        this.renderSettingsButton = this.renderSettingsButton.bind(this);
        this.renderSettings = this.renderSettings.bind(this);
        this.authenticateSpotify = this.authenticateSpotify.bind(this);
        this.getCurrentSong = this.getCurrentSong.bind(this);
        this.getRoomDetails = this.getRoomDetails.bind(this);
        this.getRoomDetails();
    }

    componentDidMount() {
        this.interval = setInterval(this.getCurrentSong, 1000);
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    /**
     * Update state with current room details
     */
    getRoomDetails() {
        fetch("/api/get-room" + "?code=" + this.roomCode)
            .then((response) => {
                if(!response.ok) {
                    this.props.leaveRoomCallback();
                    this.props.history.push("/");
                }
                return response.json()
            })
            .then((data) => {
                this.setState({
                    votesToSkip: data.votes_to_skip,
                    guestCanPause: data.guest_can_pause,
                    isHost: data.is_host,
                });
                if(this.state.isHost) {
                    this.authenticateSpotify();
                }
            });
    }

    /**
     * Updates state with info on the current song
     */
    getCurrentSong() {
        fetch("/spotify/current-song")
            .then((response) => {
                if(!response.ok) {
                    return {};
                }
                else {
                    return response.json();
                }
            })
            .then((data) => {
                this.setState({ song: data });  
            });
    }

    /**
     * Update the show settings state to provided value
     * @param {boolean} value Whether settings are currently showing
     */
    updateShowSettings(value) {
        this.setState({
            showSettings: value,
        });
    }

    /**
     * Authenticate spotify if it has not already been authenticated
     */
    authenticateSpotify() {
        fetch("/spotify/is-authenticated")
            .then((response) => response.json())
            .then((data) => {
                this.setState({ spotifyAuthenticated: data.status });
                if(!data.status) {
                    fetch("/spotify/get-auth-url")
                    .then((response) => response.json())
                    .then((data) => {
                        window.location.replace(data.url);
                    });
                }
            });
    }

    leaveButtonPressed() {
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
          };
        fetch("/api/leave-room", requestOptions).then((_response) => {
            this.props.leaveRoomCallback();
            this.props.history.push("/");
        });
    }

    renderSettingsButton() {
        return (
            <Grid item xs={12} align="center">
                <Button 
                variant="contained"
                color="primary"
                onClick={() => this.updateShowSettings(true)}>
                    Settings
                </Button>
            </Grid>
        );
    }

    renderSettings() {
        return(
            <Grid container spacing={1}>
                <CreateRoomPage 
                update={true}
                votesToSkip={this.state.votesToSkip}
                guestCanPause={this.state.guestCanPause}
                roomCode={this.roomCode}
                updateCallback={this.getRoomDetails}
                />
                <Grid item xs={12} align="center">
                    <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => this.updateShowSettings(false)}
                    >
                        Close
                    </Button>

                </Grid>
            </Grid>
        );
    }

    render() {
        if(this.state.showSettings) {
            return this.renderSettings();
        }
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Typography variant="h4" component="h4">
                        Code: { this.roomCode }
                    </Typography>
                </Grid>
                <MusicPlayer {...this.state.song}/>
                {this.state.isHost ? this.renderSettingsButton() : null }
                <Grid item xs={12} align="center">
                    <Button
                        variant="contained" 
                        color="secondary" 
                        onClick={this.leaveButtonPressed}
                    >
                        Leave Room
                    </Button>
                </Grid>
            </Grid>
        );
    }
}
