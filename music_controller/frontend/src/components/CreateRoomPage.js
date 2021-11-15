import React, {Component} from "react";
import { Link } from "react-router-dom";
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography"
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import { Collapse } from "@material-ui/core";
import Alert from "@material-ui/lab/Alert";


export default class CreateRoomPage extends Component {
    static defaultProps = {
        votesToSkip: 2,
        guestCanPause: false,
        update: false,
        roomCode: null,
        updateCallback: () => {},
    };

    constructor(props) {
        super(props);
        this.state = {
            guest_can_pause: this.props.guestCanPause,
            votes_to_skip: this.props.votesToSkip,
            successMsg: "",
            errorMsg: "",
        };
        this.handleCreateButtonClicked = this.handleCreateButtonClicked.bind(this);
        this.handleUpdateButtonClicked = this.handleUpdateButtonClicked.bind(this);
        this.handleVotesChange = this.handleVotesChange.bind(this);
        this.handlePauseChange = this.handlePauseChange.bind(this);
        
    }
    defaultVotes = 2;

    handleVotesChange(e) {
        this.setState({
            votes_to_skip: e.target.value,
        });
    }

    handlePauseChange(e) {
        this.setState({
            guest_can_pause: e.target.value,
        });
    }

    handleCreateButtonClicked() {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({
                votes_to_skip: this.state.votes_to_skip,
                guest_can_pause: this.state.guest_can_pause,
            }),
        }
        fetch("/api/create-room", requestOptions)
            .then((response) => response.json())
            .then((data) => this.props.history.push("/room/" + data.code));

    }

    handleUpdateButtonClicked() {
        const requestOptions = {
            method: "PATCH",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({
                guest_can_pause: this.state.guest_can_pause,
                votes_to_skip: this.state.votes_to_skip,
                code: this.props.roomCode,
            }),
        };
        fetch("/api/update-room", requestOptions)
            .then((response) => {
                if(response.ok) {
                    this.setState({
                        successMsg: "Room updated successfully."
                    });
                } else {
                    this.setState({
                        errorMsg: "Error updating room..."
                    });
                }
                this.props.updateCallback();
            });
    }

    renderCreateButtons() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Button color="primary" variant="contained" onClick={this.handleCreateButtonClicked}>
                        Create A Room
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

    renderUpdateButtons() {
        return (
                <Grid item xs={12} align="center">
                    <Button 
                        color="primary" 
                        variant="contained" 
                        onClick={this.handleUpdateButtonClicked}
                    >
                            Update Room
                    </Button>
                </Grid>
        );
    }

    render() {
        const title = this.props.update ? "Update Room" : "Create A Room";

        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Collapse in={this.state.errorMsg != "" || this.state.successMsg != ""}>
                        {this.state.successMsg != "" ? (
                            <Alert 
                                severity="success" 
                                onClose={() => {
                                    this.setState({successMsg: ""});
                                }}
                            >
                                {this.state.successMsg}
                            </Alert>
                        ) : (
                            <Alert 
                                severity="error" 
                                onClose={() => {
                                    this.setState({errorMsg: ""});
                                }}
                            >
                                {this.state.errorMsg}
                            </Alert>
                        )}
                    </Collapse>
                </Grid>
                <Grid item xs={12} align="center">
                    <Typography component='h4' variant='h4'>
                        {title}
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl component="fieldset">
                        <FormHelperText>
                            <div align="center">Can guests pause the music?</div>
                        </FormHelperText>
                        <RadioGroup 
                        row 
                        defualtValue={this.props.guestCanPause.toString()} 
                        onChange={this.handlePauseChange}>
                            <FormControlLabel 
                                value="true" 
                                control={<Radio color="primary"/>} 
                                label="Yes!" 
                                labelPlacement="bottom"
                            />
                            <FormControlLabel 
                                value="false" 
                                control={<Radio color="secondary"/>} 
                                label="No!" 
                                labelPlacement="bottom"
                            />
                        </RadioGroup>
                    </FormControl>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField 
                            required={true}
                            type="number"
                            onChange={this.handleVotesChange}
                            defaultValue={this.props.votesToSkip}
                            inputProps={{
                                min: 1,
                                style: {textAlign: "center"}
                            }}
                        />
                        <FormHelperText>
                            <div align="center">
                                How many votes to skip the song?
                            </div>
                        </FormHelperText>
                    </FormControl>
                </Grid>
                {this.props.update 
                ? this.renderUpdateButtons() 
                : this.renderCreateButtons()}
            </Grid>
        );
    }
}