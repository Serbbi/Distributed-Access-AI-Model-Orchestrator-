package nl.rug.cc.services;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.http.HttpRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import nl.rug.cc.services.AuthResponse.AuthResponse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.annotation.PostConstruct;

@Service
public class AuthService {
    // Class JSON handler
    private static final ObjectMapper objectMapper = new ObjectMapper();
    // Query client
    private static HttpClient client = HttpClient.newHttpClient();

    private static final Logger log = LoggerFactory.getLogger(AuthService.class);

    @Value("${ory.keto.url}")
    private String ketoUrl;

    @Value("${ory.keto.port}")
    private String ketoPort;

    @Value("${ory.kratos.url}")
    private String kratosUrl;

    @Value("${ory.kratos.port}")
    private String kratosPort;

    public String KETO_URL;

    public String KRATOS_URL;

    @PostConstruct
    public void init() {
        this.KRATOS_URL = "http://kratos.default.svc.cluster.local" + ":" + kratosPort + "/sessions/whoami";
        log.info(KRATOS_URL);
        this.KETO_URL = "http://keto.default.svc.cluster.local" + ":" + ketoPort + "/relation-tuples/check";
        log.info(KETO_URL);
    }

    /**
     * This method returns the userId from the session cookie after verifying with
     * Kratos
     */
    private String getUserIdFromSession(String cookie) throws Exception {
        log.info(KRATOS_URL);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(KRATOS_URL))
                .header("Cookie", cookie)
                .header("Content-Type", "application/json")
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        System.out.println(response);
        System.out.flush();

        if (response.statusCode() == 200) {
            JsonNode jsonResponse = objectMapper.readTree(response.body());

            return jsonResponse.get("identity").get("traits").get("email").asText();
        }
        return "N/A";
    }


    /** Determines if the user has the correct permission for specific resource */
    private boolean checkKetoPermission(String userId, String resource, String relation) throws Exception {
        String query = String.format(
                "{\"namespace\": \"resource\", \"object\": \"%s\", \"relation\": \"%s\", \"subject_id\": \"%s\"}",
                resource, relation, userId);

        System.err.println(KETO_URL);
        System.out.println(query);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(KETO_URL))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(query))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        System.err.println("KETO RESPONSE");
        System.err.println(response.body());
        System.err.flush();

        if (response.statusCode() == 200) {
            JsonNode jsonResponse = objectMapper.readTree(response.body());
            return jsonResponse.get("allowed").asBoolean();
        }

        return false;
    }



    /**
     * Checks if a valid session exists and returns an AuthResponse with userId and
     * permission
     */
    public AuthResponse userHasValidSession(String cookie) throws Exception {
        String userId = getUserIdFromSession(cookie);

        if (userId != "N/A") {
            return new AuthResponse(true, userId);
        }

        return new AuthResponse(false, null);
    }


    /** Get all resources accessible by a user for a specific type */
    /* Type should be 'models' or 'data' */
    public Set<String> getUserAccessibleResources(String cookie, String[] resources) throws Exception {
        AuthResponse hasValidSessionResponse = userHasValidSession(cookie);

        Set<String> allResources = new HashSet<>();

        if (!hasValidSessionResponse.hasPermission) {
            return allResources;
        }

        for (String resource : resources) {
            boolean userHasAccess = checkKetoPermission("user:" + hasValidSessionResponse.userId, resource, "access");
            if (userHasAccess) {
                allResources.add(resource);
            }
        }
        
        return allResources;
    }
}