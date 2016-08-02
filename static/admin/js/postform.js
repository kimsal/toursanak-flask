var temp_html='';
var image_string='';
var feature_image="";
function getAllRemoveImages(){
    $('input[name="all_removed_images"]').attr('value','');
    image_string='';
    if(img_no==0)
      img_no=1;
    for(var i=1;i<=img_no;i++){
      if($('input[name="remove'+i+'"]:checked').length>0){
        if(image_string!='')
           image_string=image_string+"$$$$$"+ $('input[name="image'+i+'"]').val();
        else
          image_string=$('input[name="image'+i+'"]').val();
      }
    }
    $('input[name="all_removed_images"]').attr('value',image_string);
  }


function loadOldImages(images){
  var arr_images=images.split('$$$$$');
  if(arr_images.length>0){
    for(var i=0;i<arr_images.length;i++){
      img_no++;
      if(arr_images[i]!=""){
        temp_html='<tr><td><input type="file" name="other_image[]" multiple=""  class="other_image'+img_no+'"/></td><td><img src="/static/images/images/'+arr_images[i]+'" class="img-responsive img-'+img_no+'" style="max-width:100px;"></td><td><input type="text" value="'+arr_images[i]+'" style="display:none;" name="image'+img_no+'" /></td><td class="delete delete'+img_no+'" onclick="removeImage('+img_no+')"><input type="checkbox" name="remove'+img_no+'" id="rm'+img_no+'"/>Remove</td></tr>';
        if(i==0)
          $("#imgs").html(temp_html);
        else
          $("#imgs").append(temp_html);
      }
      loadImage(img_no);
    }
  }
   getAllRemoveImages();
}
function loadImage(img_nom){
    if(img_nom==0)
      img_nom=1;
    $('.other_image'+img_nom).change(function(){
        readURL(this,img_nom);
    });
  }


  