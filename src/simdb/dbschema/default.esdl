module default {

    type Project {
        required property name -> str;
        required multi link simulations -> Simulation;
    }

    type Simulation {
        required property name -> str;
        required property software -> str;
    }

}