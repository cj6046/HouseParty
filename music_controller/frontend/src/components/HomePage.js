import React, {Component} from "react";
import CreateRoomPage from "./CreateRoomPage";
import JoinRoomPage from "./JoinRoomPage";
import RoomPage from "./RoomPage";
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
    }

    render() {
        return (
            <Router>
                <Switch>
                    <Route exact path="/">This is the Home page</Route>
                    <Route path="/create" component={CreateRoomPage} />
                    <Route path="/join" component={JoinRoomPage} />
                    <Route path="/room/:roomCode" component={RoomPage} />
                </Switch>
            </Router>
        );
    }
}