import React, {Component} from "react";
import CreateRoomPage from "./CreateRoomPage";
import JoinRoomPage from "./JoinRoomPage";
import RoomPage from "./RoomPage";
import {Grid, Button, ButtonGroup, Typography} from "@material-ui/core"
import { 
    BrowserRouter as Router, 
    Switch, 
    Route, 
    Link, 
    Redirect 
} from "react-router-dom";

export default class HomePage extends Component {
    constructor(props) {
        super(props);
        this.state={
            roomCode: null
        };
    }

    async componentDidMount() {
        fetch('/api/user-in-room')
        .then((response) => response.json())
        .then((data) => {this.setState({
                roomCode: data.code,
            });
        });
    }

    renderHomePage() {
        return (
            <Grid container spacing={3}>
                <Grid item xs={12} align="center">
                    <Typography component="h3" variant="h3">
                        House Party
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <ButtonGroup disableElevation variant="contained">
                        <Button color="primary" to='/join' component={Link}>
                            Join a Party
                        </Button>
                        <Button color="secondary" to='/create' component={Link}>
                            Start a Party
                        </Button>
                    </ButtonGroup>
                </Grid>
            </Grid>
        );
    }

    render() {
        return (
            <Router>
                <Switch>
                    <Route 
                    exact 
                    path="/" 
                    render={() => {
                            return this.state.roomCode ? (
                                <Redirect to={`/room/${this.state.roomCode}`}/>
                            ) : (
                                this.renderHomePage()
                            );
                        }}
                    />
                    <Route path="/create" component={CreateRoomPage} />
                    <Route path="/join" component={JoinRoomPage} />
                    <Route path="/room/:roomCode" component={RoomPage} />
                </Switch>
            </Router>
        );
    }
}