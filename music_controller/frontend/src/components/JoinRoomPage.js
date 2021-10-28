import React, {Component} from "react"
import { Link } from "react-router-dom"
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography"
import TextField from "@material-ui/core/TextField";


export default class JoinRoomPage extends Component {
    constructor(props) {
        super(props);
        this.state= {
            roomCode: "",
            error: ""
        };
        this.handleTextFieldChange = this.handleTextFieldChange.bind(this)
        this.handleJoinRoomButtonClicked = this.handleJoinRoomButtonClicked.bind(this)
    }

    handleTextFieldChange(e) {
        this.setState({
            roomCode: e.target.value
        });
    }

    handleJoinRoomButtonClicked() {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify({
                code: this.state.roomCode
            })
        };
        fetch("/api/join-room", requestOptions)
            .then((response) => {
                if(response.ok) {
                    this.props.history.push(`/room/${this.state.roomCode}`);
                } else {
                    this.setState({error: "Room not found."});
                }
            })
            .catch((error) => {
                console.log(error);
            });
    }

    render() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Typography component="h4" variant="h4">
                        Join A Party
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <TextField 
                        type="text"
                        error={this.state.error}
                        label="Code"
                        placeholder="Enter a room code"
                        value={this.state.roomCode}
                        helperText={this.state.error}
                        variant="outlined"
                        onChange={this.handleTextFieldChange}
                    />
                </Grid>
                <Grid item xs={12} align="center">
                    <Button color="primary" variant="contained" onClick={this.handleJoinRoomButtonClicked}>
                        Let's go!
                    </Button>
                </Grid>
                <Grid item xs={12} align="center">
                    <Button color="secondary" variant="contained" to="/" component={Link}>
                        Back
                    </Button>
                </Grid>
            </Grid>
        );
    }
}