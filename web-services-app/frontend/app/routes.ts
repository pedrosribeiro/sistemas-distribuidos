import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
    index("routes/home.tsx"),
    route("/status", "routes/status.tsx"),
    route("/reservar/:itinerarioId", "routes/reservar.tsx")
] satisfies RouteConfig;
