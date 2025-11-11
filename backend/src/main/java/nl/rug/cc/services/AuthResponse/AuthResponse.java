package nl.rug.cc.services.AuthResponse;

public class AuthResponse {
    public final boolean hasPermission;
    public final String userId;

    public AuthResponse(boolean hasPermission, String userId) {
        this.hasPermission = hasPermission;
        this.userId = userId;
    }
}
