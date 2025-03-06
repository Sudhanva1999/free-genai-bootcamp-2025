import { useQuery } from "@tanstack/react-query";
import { getStudyActivities } from "../services/api";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { 
  Card, 
  CardContent, 
  CardMedia, 
  Typography, 
  Grid, 
  Button, 
  Container, 
  Box, 
  CardActions,
  Dialog,
  DialogContent,
  DialogActions,
  IconButton
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

// ActivityLauncher component to display the Streamlit app in a dialog
const ActivityLauncher = ({ activity, open, onClose }) => {
  return (
    <Dialog 
      fullScreen 
      open={open} 
      onClose={onClose}
    >
      <DialogActions sx={{ p: 1, justifyContent: "flex-end" }}>
        <IconButton 
          edge="end" 
          color="inherit" 
          onClick={onClose} 
          aria-label="close"
        >
          <CloseIcon />
        </IconButton>
      </DialogActions>
      <DialogContent sx={{ p: 0, height: "100%", overflow: "hidden" }}>
        <iframe
          src={activity?.url}
          title={activity?.name}
          width="100%"
          height="100%"
          style={{ border: "none" }}
        />
      </DialogContent>
    </Dialog>
  );
};

const StudyActivities = () => {
  const navigate = useNavigate();
  const [launcherOpen, setLauncherOpen] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);

  const { data } = useQuery({
    queryKey: ["studyActivities"],
    queryFn: getStudyActivities,
  });

  console.log(data);

  const handleLaunch = (activity) => {
    setSelectedActivity(activity);
    setLauncherOpen(true);
  };

  const handleCloseLauncher = () => {
    setLauncherOpen(false);
    setSelectedActivity(null);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
          Study Activities
        </Typography>
        
        <Grid container spacing={3}>
          {data?.map((activity) => (
            <Grid item xs={12} sm={6} md={4} key={activity.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardMedia
                  component="img"
                  height="194"
                  image={activity.preview_url}
                  alt={activity.name}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h5" component="div" gutterBottom>
                    {activity.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {activity.description}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button 
                    variant="contained" 
                    onClick={() => handleLaunch(activity)}
                  >
                    Launch
                  </Button>
                  <Button 
                    variant="outlined" 
                    onClick={() => navigate(`/study_activities/${activity.id}`)}
                  >
                    View Details
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Activity Launcher Dialog */}
      <ActivityLauncher 
        activity={selectedActivity} 
        open={launcherOpen} 
        onClose={handleCloseLauncher} 
      />
    </Container>
  );
};

export default StudyActivities;