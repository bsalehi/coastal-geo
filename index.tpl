<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Geolocation</title>

    <!-- Bootstrap Core CSS -->
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link href="/static/css/sb-admin.css" rel="stylesheet">

    <!-- Morris Charts CSS -->
    <link href="/static/css/plugins/morris.css" rel="stylesheet">

    <!-- Custom Fonts -->
    <link href="/static/font-awesome/css/font-awesome.min.css" rel="stylesheet" type="text/css">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
        <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
        <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->

    <style>
       #map {
        height: 400px;
        width: 100%;
       }
    </style>

  
  
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>





</head>

<body>

    <div id="wrapper">


        <div id="page-wrapper">

            <div class="container-fluid">

                <!-- Page Heading -->
                <div class="row">
                    <div class="col-lg-12">
                        <h2 class="page-header">
                            GeoLocation
                        </h2>
                        <div class="alert alert-info alert-dismissable">
                                	<form action="/map" method="post">
                                        <table><tr>
                                        <td width="40%">
                                        <div class="input-group">
                                            <span class="input-group-addon">Twitter Account</span> <input name="name" type="text" value="{{accountName}}"/>
                                        </div>
                                        </td width="10%">
                                        <td>
                                        OR
                                        </td>
                                        <td width="45%">
                                        <div class="input-group">
                                            <span class="input-group-addon">Text</span> <input size="60" name="tweet" value="{{filledText}}" />
                                        </div>
                                        </td>
                                        <td width="5%">                
                                        <input type="submit" class="btn btn-success" value="GeoLocate!" type="submit" />
                                        </td></tr>
                                        </table>
                                        </form>
                        </div>
                    </div>
                </div>
                <!-- /.row -->
                <!-- /.row -->

                <div class="row">
                    <div class="col-lg-4 col-md-4">
                        <div class="panel panel-primary">
                            <div class="panel-heading">
                                <div class="row">
                                    <div class="col-xs-3">
                                        <div>MAP</div>
                                    </div>
                                    <div class="col-xs-9">
                                    Our Prediction is: <strong><font color="#FF0000">{{city}}</font></strong>
                                    </div>
                                </div>
                            </div>
                            <div id="map"></div>
                                <script>
                                  function initMap() {
                                    var uluru = {lat: {{lats[0]}}, lng: {{longs[0]}}};
                                    var map = new google.maps.Map(document.getElementById('map'), {
                                      zoom: 4,
                                  center: uluru
                                  });                        
                                    var marker = new google.maps.Marker({
                                      position: uluru,
                                      map: map
                                });
                            }    
                        </script>

                            <script async defer
                                src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDMq2g0P2_jGgEgYH9RXa_LlZ0YREsxxBU&callback=initMap">
                            </script>

                            Next predictions are:
                                
                                    %for c in cities:
                                    	<li>{{c}}</li>
                                    %end

                        </div>
                    </div>
                    
                    <div class="col-lg-8 col-md-8">
                        <div class="panel panel-green">
                            <div class="panel-heading">
                                <div class="row">
                                    <div class="col-xs-3">
                                        <div>The Input text is:</div>
                                    </div>
                                </div>
                            </div>
                                <div class="panel-footer">
                                    {{text}} ...
                                    <div class="clearfix"></div>
                                </div>
                            
                        </div>
                    </div>

                    <div class="col-lg-2 col-md-2">
                        <div class="panel panel-red">
                            <div class="panel-heading">
                                <div class="row">
                                    <div class="col-xs-12">
                                        <div>Network:</div>
                                    </div>
                                </div>
                            </div>
                            
                                <div class="panel-footer">                                    
                                    
                                    %for c in mentionsLocs:
                                    	<li>{{c}}</li>
                                    %end
                                </div>
                            
                        </div>
                    </div>
                    


                <div class="col-lg-2 col-md-2">
                        <div class="panel panel-yellow">
                            <div class="panel-heading">
                                <div class="row">
                                    <div class="col-xs-12">
                                        <div>Indicative words are:</div>
                                    </div>
                                </div>
                            </div>
                            
                                <div class="panel-footer">

                                  
                                    <ul>
                                    %for item in features:
                                        <li>{{item[0]}}</li>
                                    %end
                                    </ul>

                                    <div class="clearfix"></div>
                                </div>
                            
                        </div>
                    </div>




                <div class="col-lg-2 col-md-2">
                        <div class="panel panel-yellow">
                            <div class="panel-heading">
                                <div class="row">
                                    <div class="col-xs-12">
                                        <div>Low entropy words are:</div>
                                    </div>
                                </div>
                            </div>
                            
                                <div class="panel-footer">
                                  
                                    <ul>
                                    %for item in entropy:
                                        <li>{{item[0]}}</li>
                                    %end
                                    </ul>


                                    <div class="clearfix"></div>
                                </div>
                            
                        </div>
                    </div>


                    <div class="col-lg-2 col-md-2">
                        <div class="panel panel-yellow">
                            <div class="panel-heading">
                                <div class="row">
                                    <div class="col-xs-12">
                                        <div>High KL words are:</div>
                                    </div>
                                </div>
                            </div>
                            
                                <div class="panel-footer">

                                  
                                    <ul>
                                    %for item in KLD:
                                        <li>{{item[0]}}</li>
                                    %end
                                    </ul>


                                    <div class="clearfix"></div>
                                </div>
                            
                        </div>
                    </div>


                    
                </div>
                <!-- /.row -->

                <!-- /.row -->

            </div>
            <!-- /.container-fluid -->

        </div>
        <!-- /#page-wrapper -->

    </div>
    <!-- /#wrapper -->

    <!-- jQuery -->
    <script src="js/jquery.js"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="js/bootstrap.min.js"></script>

    <!-- Morris Charts JavaScript -->
    <script src="js/plugins/morris/raphael.min.js"></script>
    <script src="js/plugins/morris/morris.min.js"></script>
    <script src="js/plugins/morris/morris-data.js"></script>

</body>

</html>
