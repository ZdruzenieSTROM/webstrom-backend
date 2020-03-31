from django.db import models
from base.models import ContentTypeRestrictedFileField
# Create your models here.

class Competition(models.Model):
    class Meta:
        verbose_name = 'seminár'
        verbose_name_plural = 'semináre'
    
    name = models.CharField(max_length=50, verbose_name='názov')
    start_year = models.PositiveSmallIntegerField(
        verbose_name='rok prvého ročníka súťaže'
        )
    
class Semester(models.Model):
    class Meta:
        verbose_name='semester'
        verbose_name_plural='semestre'
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(
        verbose_name='ročník'
        )
    start = models.DateTimeField(verbose_name='dátum začiatku semestra')
    end = models.DateTimeField(verbose_name='dátum konca semestra')
    late_tags = models.ManyToManyField(LateTag, verbose_name='')
    season = models.CharField(max_length=10, choices = ['zimný semester', 'letný semester'])

class Series(models.Model):
    class Meta:
        verbose_name='séria'
        verbose_name_plural='série'
    
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name='poradie série')
    deadline = models.DateTimeField(verbose_name='termín série')
    complete = models.BooleanField(verbose_name='séria uzavretá')
    sum_method = # NO FOKEN IDEA

class LateTag(models.Model):
    class Meta:
        verbose_name='séria'
        verbose_name_plural='série'

    name = models.CharField(max_length=50, verbose_name='označenie štítku pre riešiteľa')
    upper_bound = models.DurationField(verbose_name='maximálna dĺžka omeškania')
    comment = models.TextField(verbose_name='komentár pre opravovateľa')


class Solution(models.Model):
    class Meta:
        verbose_name='riešenie'
        verbose_name_plural='riešenia'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user_semester_registration = models.ForeignKey(
        UserSemesterRegistration, 
        on_delete=models.CASCADE
        )
    solution_path = # File field - isteho typu

    corrected_solution_path = # File field - isteho typu

    score = models.PositiveSmallIntegerField(verbose_name='body')

    uploaded_at = DateTimeField(auto_now=True, verbose_name='nahrané dňa')

    # V prípade, že riešenie prišlo po termíne nastaví sa na príslušný tag
    late_tag = models.ForeignKey(
        LateTag, 
        on_delete=models.SET_NULL
        verbose_name='',
        null = True,
        blank = True)

    is_online = models.BooleanField(
        verbose_name = 'internetové riešenie'
    )


class Problem(models.Model):
    class Meta:
        verbose_name='úloha'
        verbose_name_plural='úlohy'

    problem = models.TextField(verbose_name='znenie úlohy')
    serie = models.ForeignKey(
        Series, 
        on_delete=models.cascade, 
        verbose_name='úloha zaradená do série'
        )
    order = models.PositiveSmallIntegerField(verbose_name='poradie v sérii')


class UserSemesterRegistration(models.Model):
    class Meta:
        verbose_name='séria'
        verbose_name_plural='série'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    school = models.ForeignKey('user.School', on_delete=models.SET_NULL, null=True)
    class_level = models.ForeignKey(Grade, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def register_user(user):
        #TODO:Vytvorí novú registráciu userovi


    

